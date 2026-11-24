import type { GeoJsonPolygon, QuintaMap } from "@/lib/production";

export type MapInteractionMode = "view" | "edit";

export type PolygonTarget =
  { kind: "quinta" } | { kind: "vidriera"; id: string };

export type PolygonClickEffect =
  | { type: "navigate"; href: string }
  | { type: "select"; id: string }
  | { type: "none" };

export type OverviewPolygon =
  | { kind: "quinta"; geometry: GeoJsonPolygon }
  | {
      kind: "vidriera";
      id: string;
      code: string;
      active: boolean;
      geometry: GeoJsonPolygon;
    };

export function vidrieraDetailHref(id: string): string {
  return `/produccion/vidrieras/${id}`;
}

export function polygonClickEffect(
  mode: MapInteractionMode,
  target: PolygonTarget,
): PolygonClickEffect {
  if (target.kind === "quinta") {
    return { type: "none" };
  }
  if (mode === "view") {
    return { type: "navigate", href: vidrieraDetailHref(target.id) };
  }
  return { type: "select", id: target.id };
}

export function dispatchPolygonClick(
  mode: MapInteractionMode,
  target: PolygonTarget,
  actions: {
    navigate: (href: string) => void;
    select: (id: string) => void;
  },
): void {
  const effect = polygonClickEffect(mode, target);
  if (effect.type === "navigate") {
    actions.navigate(effect.href);
  }
  if (effect.type === "select") {
    actions.select(effect.id);
  }
}

export function polygonsForOverview(data: QuintaMap): OverviewPolygon[] {
  const polygons: OverviewPolygon[] = [];
  if (data.geometry) {
    polygons.push({ kind: "quinta", geometry: data.geometry });
  }
  for (const vidriera of data.vidrieras) {
    if (!vidriera.geometry) {
      continue;
    }
    polygons.push({
      kind: "vidriera",
      id: vidriera.id,
      code: vidriera.code,
      active: vidriera.active,
      geometry: vidriera.geometry,
    });
  }
  return polygons;
}
