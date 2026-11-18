"use client";

import { useEffect, useRef, useState } from "react";
import type { Map as LeafletMap } from "leaflet";
import "leaflet/dist/leaflet.css";

import {
  INITIAL_CAMERA,
  type ImageryPublicConfig,
  type PlaceSearchResult,
} from "@/lib/imagery";
import type { GeoJsonPolygon, QuintaMap } from "@/lib/production";
import { MapStatus } from "./map-status";

export function FarmMap({
  mapData,
  imagery,
}: {
  mapData: QuintaMap;
  imagery: ImageryPublicConfig;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<LeafletMap | null>(null);
  const [tileError, setTileError] = useState(false);
  const [mapFailed, setMapFailed] = useState(false);
  const [geometryError, setGeometryError] = useState(false);
  const [query, setQuery] = useState("");
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [results, setResults] = useState<PlaceSearchResult[]>([]);
  const hasBoundary =
    mapData.geometry !== null ||
    mapData.vidrieras.some((vidriera) => vidriera.geometry !== null);

  useEffect(() => {
    const element = containerRef.current;
    if (!element) {
      return;
    }
    let disposed = false;
    let map: LeafletMap | null = null;

    void import("leaflet")
      .then((leaflet) => {
        if (disposed) {
          return;
        }
        map = leaflet.map(element, {
          zoomControl: true,
          minZoom: imagery.minZoom,
          maxZoom: imagery.maxZoom,
        });
        mapRef.current = map;
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
        const group = leaflet.featureGroup();
        const drew = [
          addPolygon(leaflet, group, mapData.geometry, {
            color: "#1f6b45",
            weight: 3,
            fillColor: "#1f6b45",
            fillOpacity: 0.08,
          }),
          ...mapData.vidrieras.map((vidriera) =>
            addPolygon(leaflet, group, vidriera.geometry, {
              color: vidriera.active ? "#174f33" : "#4d5a53",
              weight: 2,
              fillColor: vidriera.active ? "#1f6b45" : "#4d5a53",
              fillOpacity: 0.28,
            }),
          ),
        ];
        if (drew.some((ok) => !ok)) {
          setGeometryError(true);
        }
        group.addTo(map);
        if (group.getLayers().length > 0) {
          map.fitBounds(group.getBounds(), { padding: [28, 28] });
        } else {
          map.setView(
            [INITIAL_CAMERA.latitude, INITIAL_CAMERA.longitude],
            INITIAL_CAMERA.zoom,
          );
        }
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
    };
  }, [imagery, mapData]);

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
  );
}

function addPolygon(
  leaflet: typeof import("leaflet"),
  group: import("leaflet").FeatureGroup,
  geometry: GeoJsonPolygon | null,
  style: import("leaflet").PathOptions,
): boolean {
  if (!geometry) {
    return true;
  }
  try {
    leaflet.geoJSON(geometry, { style: () => style }).addTo(group);
    return true;
  } catch {
    return false;
  }
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
