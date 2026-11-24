"use client";

import dynamic from "next/dynamic";

import type { QuintaMap } from "@/lib/production";

const FarmOverviewMap = dynamic(
  () => import("./farm-overview-map").then((mod) => mod.FarmOverviewMap),
  {
    ssr: false,
    loading: () => <p className="text-sm text-muted">Cargando el mapa…</p>,
  },
);

export function FarmOverviewLoader({ mapData }: { mapData: QuintaMap }) {
  return <FarmOverviewMap mapData={mapData} />;
}
