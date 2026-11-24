"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import type {} from "@geoman-io/leaflet-geoman-free";
import type { FeatureGroup, Map as LeafletMap, Polygon } from "leaflet";
import "leaflet/dist/leaflet.css";
import "@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css";

import {
  createVidrieraRecord,
  loadNextVidrieraCode,
  removeBoundary,
  saveBoundary,
} from "@/app/produccion/map-actions";
import {
  INITIAL_CAMERA,
  type ImageryPublicConfig,
  type PlaceSearchResult,
} from "@/lib/imagery";
import type {
  BoundaryWarning,
  GeoJsonPolygon,
  QuintaMap,
} from "@/lib/production";
import { dispatchPolygonClick } from "@/lib/map-interaction";
import { MapEditorPanel, type MapDraft } from "./map-editor-panel";
import { placePolygon } from "./map-geometry";
import { MapStatus } from "./map-status";

type LeafletModule = typeof import("leaflet");
type Drawable = Polygon & {
  pm?: {
    enable: (options?: { allowSelfIntersection?: boolean }) => void;
    disable: () => void;
  };
};
type PmMap = LeafletMap & {
  pm: {
    setLang: (lang: "es") => void;
    enableDraw: (
      shape: "Polygon",
      options?: { allowSelfIntersection?: boolean; snappable?: boolean },
    ) => void;
    disableDraw: () => void;
  };
};

export function FarmMap({
  mapData,
  imagery,
  justCreated = false,
}: {
  mapData: QuintaMap;
  imagery: ImageryPublicConfig;
  justCreated?: boolean;
}) {
  const router = useRouter();
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<PmMap | null>(null);
  const leafletRef = useRef<LeafletModule | null>(null);
  const savedGroupRef = useRef<FeatureGroup | null>(null);
  const quintaLayerRef = useRef<Drawable | null>(null);
  const vidrieraLayersRef = useRef<Map<string, Drawable>>(new Map());
  const draftLayerRef = useRef<Drawable | null>(null);
  const activeLayerRef = useRef<Drawable | null>(null);
  const draftRef = useRef<MapDraft | null>(null);
  const fittedData = useRef<QuintaMap | null>(null);
  const [mapReady, setMapReady] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [tileError, setTileError] = useState(false);
  const [mapFailed, setMapFailed] = useState(false);
  const [geometryError, setGeometryError] = useState(false);
  const [query, setQuery] = useState("");
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [results, setResults] = useState<PlaceSearchResult[]>([]);
  const [draft, setDraftState] = useState<MapDraft | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notices, setNotices] = useState<BoundaryWarning[]>([]);
  const [confirmingRemoval, setConfirmingRemoval] = useState<string | null>(
    null,
  );
  const hasBoundary =
    mapData.geometry !== null ||
    mapData.vidrieras.some((vidriera) => vidriera.geometry !== null);

  function setDraft(next: MapDraft | null) {
    draftRef.current = next;
    setDraftState(next);
  }

  function renderSaved(
    data: QuintaMap,
    activeId: string | null,
    fitView: boolean,
  ) {
    const leaflet = leafletRef.current;
    const map = mapRef.current;
    const group = savedGroupRef.current;
    if (!leaflet || !map || !group) {
      return;
    }
    draftLayerRef.current?.remove();
    draftLayerRef.current = null;
    activeLayerRef.current = null;
    group.clearLayers();
    quintaLayerRef.current = null;
    vidrieraLayersRef.current = new Map();
    let broken = !placePolygon(
      leaflet,
      group,
      data.geometry,
      {
        color: "#1f6b45",
        weight: 3,
        fillColor: "#1f6b45",
        fillOpacity: 0.08,
      },
      (layer) => {
        quintaLayerRef.current = layer;
      },
    );
    for (const vidriera of data.vidrieras) {
      const selected = vidriera.id === activeId;
      const placed = placePolygon(
        leaflet,
        group,
        vidriera.geometry,
        {
          color: vidriera.active ? "#174f33" : "#4d5a53",
          weight: selected ? 4 : 2,
          fillColor: vidriera.active ? "#1f6b45" : "#4d5a53",
          fillOpacity: selected ? 0.45 : 0.28,
        },
        (layer) => {
          vidrieraLayersRef.current.set(vidriera.id, layer);
          layer.bindTooltip(vidriera.code, {
            permanent: true,
            direction: "center",
            className: "vidriera-code-label",
            opacity: 1,
          });
          layer.on("click", () => {
            dispatchPolygonClick(
              "edit",
              { kind: "vidriera", id: vidriera.id },
              {
                navigate: () => undefined,
                select: setSelectedId,
              },
            );
          });
        },
      );
      broken = broken || !placed;
    }
    setGeometryError(broken);
    if (!fitView) {
      return;
    }
    if (group.getLayers().length > 0) {
      map.fitBounds(group.getBounds(), { padding: [28, 28] });
    } else {
      map.setView(
        [INITIAL_CAMERA.latitude, INITIAL_CAMERA.longitude],
        INITIAL_CAMERA.zoom,
      );
    }
  }

  useEffect(() => {
    const element = containerRef.current;
    if (!element) {
      return;
    }
    let disposed = false;
    let map: PmMap | null = null;

    void import("leaflet")
      .then(async (leaflet) => {
        await import("@geoman-io/leaflet-geoman-free");
        if (disposed || !containerRef.current) {
          return;
        }
        leafletRef.current = leaflet;
        map = leaflet.map(containerRef.current, {
          zoomControl: true,
          minZoom: imagery.minZoom,
          maxZoom: imagery.maxZoom,
        }) as PmMap;
        if (!map.pm) {
          setMapFailed(true);
          return;
        }
        map.pm.setLang("es");
        mapRef.current = map;
        savedGroupRef.current = leaflet.featureGroup().addTo(map);
        if (imagery.configured && imagery.tileUrl && imagery.attribution) {
          leaflet
            .tileLayer(imagery.tileUrl, {
              attribution: imagery.attribution,
              tileSize: imagery.tileSize,
              zoomOffset: imagery.zoomOffset,
              minZoom: imagery.minZoom,
              maxZoom: imagery.maxZoom,
            })
            .on("tileerror", () => {
              if (!disposed) {
                setTileError(true);
              }
            })
            .addTo(map);
        }
        map.on("pm:create", (event) => {
          const created = event.layer;
          if (!(created instanceof leaflet.Polygon)) {
            created.remove();
            return;
          }
          const layer = created as Drawable;
          draftLayerRef.current?.remove();
          draftLayerRef.current = layer;
          activeLayerRef.current = layer;
          layer.pm?.enable({ allowSelfIntersection: false });
          setDraftState((current) => {
            if (!current) {
              return current;
            }
            const next = { ...current, phase: "ready" as const };
            draftRef.current = next;
            return next;
          });
        });
        setMapReady(true);
        window.requestAnimationFrame(() => map?.invalidateSize());
      })
      .catch(() => {
        if (!disposed) {
          setMapFailed(true);
        }
      });

    return () => {
      disposed = true;
      map?.remove();
      mapRef.current = null;
      setMapReady(false);
    };
  }, [
    imagery.attribution,
    imagery.configured,
    imagery.maxZoom,
    imagery.minZoom,
    imagery.tileSize,
    imagery.tileUrl,
    imagery.zoomOffset,
  ]);

  useEffect(() => {
    if (!mapReady || draftRef.current) {
      return;
    }
    renderSaved(mapData, selectedId, fittedData.current !== mapData);
    fittedData.current = mapData;
  }, [mapReady, mapData, selectedId]);

  function beginDraw(next: MapDraft) {
    const map = mapRef.current;
    if (!map?.pm) {
      setError("El mapa todavía no está listo.");
      return;
    }
    setError(null);
    setNotices([]);
    setConfirmingRemoval(null);
    setDraft(next);
    map.pm.disableDraw();
    map.pm.enableDraw("Polygon", {
      snappable: false,
      allowSelfIntersection: false,
    });
  }

  function cancelDraft() {
    mapRef.current?.pm.disableDraw();
    activeLayerRef.current?.pm?.disable();
    draftLayerRef.current?.remove();
    draftLayerRef.current = null;
    activeLayerRef.current = null;
    setDraft(null);
    renderSaved(mapData, selectedId, false);
  }

  async function saveDraft() {
    const current = draftRef.current;
    const layer = activeLayerRef.current;
    if (!current || current.phase !== "ready" || !layer) {
      setError("Dibuje y cierre el polígono antes de guardarlo.");
      return;
    }
    const geometry = geometryFromLayer(layer);
    if (!geometry) {
      setError("El trazado no es un polígono válido.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      if (current.kind === "quinta") {
        const result = await saveBoundary(
          "quintas",
          mapData.id,
          geometry,
          current.mode,
        );
        if (!result.ok) {
          setError(result.message);
          return;
        }
        setNotices(result.warnings);
        cancelDraft();
        router.refresh();
        return;
      }
      let vidrieraId = current.vidrieraId;
      if (!vidrieraId) {
        if (!current.name.trim() || !current.code.trim()) {
          setError("El código y el nombre de la vidriera son obligatorios.");
          return;
        }
        const created = await createVidrieraRecord(
          mapData.id,
          current.code,
          current.name,
        );
        if (!created.ok) {
          setError(created.message);
          return;
        }
        vidrieraId = created.id;
        const persisted: MapDraft = {
          ...current,
          vidrieraId,
          code: created.code,
        };
        setDraft(persisted);
      }
      const result = await saveBoundary(
        "vidrieras",
        vidrieraId,
        geometry,
        current.mode,
      );
      if (!result.ok) {
        setError(
          current.vidrieraId
            ? result.message
            : `${result.message} La vidriera quedó creada, sin polígono. Guarde de nuevo para adjuntarlo; no se creará otra.`,
        );
        if (!current.vidrieraId) {
          router.refresh();
        }
        return;
      }
      setNotices(result.warnings);
      cancelDraft();
      router.refresh();
    } finally {
      setSaving(false);
    }
  }

  async function confirmRemoval() {
    if (!confirmingRemoval) {
      return;
    }
    const kind = confirmingRemoval === "quinta" ? "quintas" : "vidrieras";
    const id = confirmingRemoval === "quinta" ? mapData.id : confirmingRemoval;
    setSaving(true);
    setError(null);
    try {
      const result = await removeBoundary(kind, id);
      if (!result.ok) {
        setError(result.message);
        return;
      }
      setConfirmingRemoval(null);
      router.refresh();
    } finally {
      setSaving(false);
    }
  }

  async function search() {
    const trimmed = query.trim();
    if (trimmed.length < 2) {
      setSearchError("Escriba al menos dos caracteres para buscar un lugar.");
      setResults([]);
      return;
    }
    setSearching(true);
    setSearchError(null);
    try {
      const response = await fetch(
        `/api/imagery/search?q=${encodeURIComponent(trimmed)}`,
      );
      const body: unknown = await response.json().catch(() => null);
      if (!response.ok) {
        setResults([]);
        setSearchError(readDetail(body));
        return;
      }
      const found = readResults(body);
      setResults(found);
      if (found.length === 0) {
        setSearchError("No se encontró ese lugar. Pruebe con otro nombre.");
      }
    } catch {
      setResults([]);
      setSearchError(
        "No se pudo buscar el lugar. El mapa guardado sigue igual.",
      );
    } finally {
      setSearching(false);
    }
  }

  return (
    <div className="grid items-start gap-4 lg:grid-cols-[22rem_minmax(0,1fr)]">
      <MapEditorPanel
        mapData={mapData}
        justCreated={justCreated}
        draft={draft}
        saving={saving}
        error={error}
        notices={notices}
        confirmingRemoval={confirmingRemoval}
        selectedId={selectedId}
        onSelectVidriera={setSelectedId}
        onDrawQuinta={() =>
          beginDraw({ kind: "quinta", mode: "attach", phase: "drawing" })
        }
        onEditQuinta={() => {
          const layer = quintaLayerRef.current;
          if (!layer?.pm) {
            setError("No se encontró el límite para editarlo.");
            return;
          }
          layer.pm.enable({ allowSelfIntersection: false });
          activeLayerRef.current = layer;
          setDraft({ kind: "quinta", mode: "replace", phase: "ready" });
        }}
        onRedrawQuinta={() => {
          quintaLayerRef.current?.remove();
          quintaLayerRef.current = null;
          beginDraw({ kind: "quinta", mode: "replace", phase: "drawing" });
        }}
        onAskRemove={setConfirmingRemoval}
        onConfirmRemove={() => {
          void confirmRemoval();
        }}
        onCancelRemove={() => setConfirmingRemoval(null)}
        onDrawVidriera={(vidrieraId) => {
          const vidriera = mapData.vidrieras.find(
            (item) => item.id === vidrieraId,
          );
          if (!vidriera) {
            return;
          }
          beginDraw({
            kind: "vidriera",
            mode: "attach",
            vidrieraId,
            code: vidriera.code,
            name: vidriera.name,
            phase: "drawing",
          });
        }}
        onEditVidriera={(vidrieraId) => {
          const layer = vidrieraLayersRef.current.get(vidrieraId);
          const vidriera = mapData.vidrieras.find(
            (item) => item.id === vidrieraId,
          );
          if (!layer?.pm || !vidriera) {
            setError("No se encontró el polígono para editarlo.");
            return;
          }
          layer.pm.enable({ allowSelfIntersection: false });
          activeLayerRef.current = layer;
          setDraft({
            kind: "vidriera",
            mode: "replace",
            vidrieraId,
            code: vidriera.code,
            name: vidriera.name,
            phase: "ready",
          });
        }}
        onRemoveVidriera={setConfirmingRemoval}
        onNewVidriera={() => {
          void loadNextVidrieraCode(mapData.id).then((next) => {
            if (!next.ok) {
              setError(next.message);
              return;
            }
            setDraft({
              kind: "vidriera",
              mode: "attach",
              vidrieraId: null,
              code: next.code,
              name: "",
              phase: "details",
            });
          });
        }}
        onDraftCode={(code) => {
          setDraftState((current) => {
            if (!current || current.kind !== "vidriera") {
              return current;
            }
            const next = { ...current, code };
            draftRef.current = next;
            return next;
          });
        }}
        onDraftName={(name) => {
          setDraftState((current) => {
            if (!current || current.kind !== "vidriera") {
              return current;
            }
            const next = { ...current, name };
            draftRef.current = next;
            return next;
          });
        }}
        onBeginDraw={() => {
          setDraftState((current) => {
            if (!current) {
              return current;
            }
            const next = { ...current, phase: "drawing" as const };
            draftRef.current = next;
            mapRef.current?.pm.disableDraw();
            mapRef.current?.pm.enableDraw("Polygon", {
              snappable: false,
              allowSelfIntersection: false,
            });
            return next;
          });
        }}
        onSave={() => {
          void saveDraft();
        }}
        onCancel={cancelDraft}
      />
      <div className="space-y-4">
        <MapStatus
          imagery={imagery}
          tileError={tileError}
          mapFailed={mapFailed}
          geometryError={geometryError}
          hasBoundary={hasBoundary}
          query={query}
          onQueryChange={setQuery}
          onSearch={() => {
            void search();
          }}
          searching={searching}
          searchError={searchError}
          results={results}
          onSelectResult={(result) => {
            mapRef.current?.flyTo(
              [result.latitude, result.longitude],
              Math.min(16, imagery.maxZoom),
            );
          }}
        />
        <div
          ref={containerRef}
          className="h-[640px] w-full overflow-hidden rounded-lg border border-line bg-[#d5ddd6]"
          role="application"
          aria-label={`Mapa de ${mapData.name}`}
        />
      </div>
    </div>
  );
}

function geometryFromLayer(layer: {
  toGeoJSON?: () => unknown;
}): GeoJsonPolygon | null {
  const feature = layer.toGeoJSON?.();
  if (!feature || typeof feature !== "object" || !("geometry" in feature)) {
    return null;
  }
  const geometry = feature.geometry;
  if (
    !geometry ||
    typeof geometry !== "object" ||
    !("type" in geometry) ||
    geometry.type !== "Polygon" ||
    !("coordinates" in geometry)
  ) {
    return null;
  }
  return geometry as GeoJsonPolygon;
}

function readDetail(body: unknown): string {
  if (
    typeof body === "object" &&
    body !== null &&
    "detail" in body &&
    typeof body.detail === "string" &&
    body.detail.trim()
  ) {
    return body.detail;
  }
  return "No se pudo buscar el lugar.";
}

function readResults(body: unknown): PlaceSearchResult[] {
  if (
    typeof body !== "object" ||
    body === null ||
    !("results" in body) ||
    !Array.isArray(body.results)
  ) {
    return [];
  }
  return body.results.flatMap((item) => {
    if (
      typeof item !== "object" ||
      item === null ||
      typeof item.label !== "string" ||
      typeof item.latitude !== "number" ||
      typeof item.longitude !== "number"
    ) {
      return [];
    }
    return [
      {
        label: item.label,
        latitude: item.latitude,
        longitude: item.longitude,
      },
    ];
  });
}
