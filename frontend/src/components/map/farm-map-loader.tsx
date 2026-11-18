"use client";

import dynamic from "next/dynamic";

import type { ImageryPublicConfig } from "@/lib/imagery";
import type { QuintaMap } from "@/lib/production";

const FarmMap = dynamic(() => import("./farm-map").then((mod) => mod.FarmMap), {
  ssr: false,
  loading: () => <p className="text-sm text-muted">Cargando el mapa…</p>,
});

export function FarmMapLoader(props: {
  mapData: QuintaMap;
  imagery: ImageryPublicConfig;
}) {
  return <FarmMap {...props} />;
}
