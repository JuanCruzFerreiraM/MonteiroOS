import type { FeatureGroup, PathOptions, Polygon } from "leaflet";

import type { GeoJsonPolygon } from "@/lib/production";

export type LeafletModule = typeof import("leaflet");

export function placePolygon(
  leaflet: LeafletModule,
  group: FeatureGroup,
  geometry: GeoJsonPolygon | null,
  style: PathOptions,
  keep: (layer: Polygon) => void,
): boolean {
  if (!geometry) {
    return true;
  }
  try {
    const collection = leaflet.geoJSON(geometry, { style: () => style });
    const layer = collection.getLayers()[0];
    if (!(layer instanceof leaflet.Polygon)) {
      return false;
    }
    group.addLayer(layer);
    keep(layer);
    return true;
  } catch {
    return false;
  }
}
