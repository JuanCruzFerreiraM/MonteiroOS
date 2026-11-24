"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import type { Map as LeafletMap, Polygon } from "leaflet";
import "leaflet/dist/leaflet.css";

import {
  dispatchPolygonClick,
  polygonsForOverview,
} from "@/lib/map-interaction";
import type { QuintaMap } from "@/lib/production";
import { placePolygon } from "./map-geometry";

export function FarmOverviewMap({ mapData }: { mapData: QuintaMap }) {
  const router = useRouter();
  const containerRef = useRef<HTMLDivElement>(null);
  const navigateRef = useRef(router.push);
  const [failed, setFailed] = useState(false);
  const [geometryError, setGeometryError] = useState(false);

  useEffect(() => {
    navigateRef.current = router.push;
  });

  useEffect(() => {
    const element = containerRef.current;
    if (!element) {
      return;
    }
    let disposed = false;
    let map: LeafletMap | null = null;

    void import("leaflet")
      .then((leaflet) => {
        if (disposed || !containerRef.current) {
          return;
        }
        map = leaflet.map(containerRef.current, {
          zoomControl: true,
          attributionControl: false,
          minZoom: 2,
          maxZoom: 20,
        });
        const group = leaflet.featureGroup().addTo(map);
        const quintaBounds: { layer: Polygon | null } = { layer: null };
        let broken = false;
        for (const polygon of polygonsForOverview(mapData)) {
          if (polygon.kind === "quinta") {
            const placed = placePolygon(
              leaflet,
              group,
              polygon.geometry,
              {
                color: "#1f6b45",
                weight: 2,
                fillColor: "#1f6b45",
                fillOpacity: 0.06,
              },
              (layer) => {
                quintaBounds.layer = layer;
              },
            );
            broken = broken || !placed;
            continue;
          }
          const base = {
            color: polygon.active ? "#174f33" : "#4d5a53",
            weight: 2,
            fillColor: polygon.active ? "#1f6b45" : "#4d5a53",
            fillOpacity: 0.35,
            className: "vidriera-polygon",
          };
          const placed = placePolygon(
            leaflet,
            group,
            polygon.geometry,
            base,
            (layer) => {
              layer.bindTooltip(polygon.code, {
                permanent: true,
                direction: "center",
                className: "vidriera-code-label",
                opacity: 1,
              });
              layer.on("mouseover", () => {
                layer.setStyle({ ...base, weight: 4, fillOpacity: 0.55 });
                layer.bringToFront();
              });
              layer.on("mouseout", () => {
                layer.setStyle(base);
              });
              layer.on("click", () => {
                dispatchPolygonClick(
                  "view",
                  { kind: "vidriera", id: polygon.id },
                  {
                    navigate: (href) => navigateRef.current(href),
                    select: () => undefined,
                  },
                );
              });
            },
          );
          broken = broken || !placed;
        }
        if (!disposed) {
          setGeometryError(broken);
        }
        const fit = () => {
          if (!map) {
            return;
          }
          const frame = quintaBounds.layer;
          if (frame) {
            map.fitBounds(frame.getBounds(), { padding: [36, 36] });
            return;
          }
          if (group.getLayers().length > 0) {
            map.fitBounds(group.getBounds(), { padding: [36, 36] });
          }
        };
        fit();
        window.requestAnimationFrame(() => {
          map?.invalidateSize();
          fit();
        });
      })
      .catch(() => {
        if (!disposed) {
          setFailed(true);
        }
      });

    return () => {
      disposed = true;
      map?.remove();
    };
  }, [mapData]);

  if (failed) {
    return (
      <p role="alert" className="text-sm leading-6 text-warning">
        No se pudo mostrar el mapa. Las vidrieras siguen en el listado.
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {geometryError ? (
        <p role="alert" className="text-sm leading-6 text-warning">
          Hay un límite guardado que no se pudo dibujar. No se modificó.
        </p>
      ) : null}
      <div
        ref={containerRef}
        className="farm-overview-map h-[36rem] w-full overflow-hidden rounded-lg border border-line bg-white"
        role="application"
        aria-label={`Mapa de ${mapData.name}`}
      />
    </div>
  );
}
