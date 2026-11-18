import Link from "next/link";

import { FarmMapLoader } from "@/components/map/farm-map-loader";
import { StatusBadge } from "@/components/production/production-views";
import { readJson } from "@/lib/backend";
import { loadImageryConfig } from "@/lib/imagery-server";
import type { QuintaMap } from "@/lib/production";

export const dynamic = "force-dynamic";

export default async function QuintaMapPage({
  params,
}: {
  params: Promise<{ quintaId: string }>;
}) {
  const { quintaId } = await params;
  const [mapResult, imagery] = await Promise.all([
    readJson<QuintaMap>(
      `/api/production/quintas/${quintaId}/map?include_inactive=true`,
    ),
    loadImageryConfig(),
  ]);

  if (!mapResult.ok) {
    return (
      <div className="space-y-4">
        <Link
          href="/produccion"
          className="text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
        >
          Volver al listado de producción
        </Link>
        <p role="alert">{mapResult.message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm text-muted">{mapResult.data.code}</p>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-semibold">{mapResult.data.name}</h2>
            <StatusBadge active={mapResult.data.active} />
          </div>
        </div>
        <Link
          href={`/produccion/quintas/${quintaId}`}
          className="text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
        >
          Volver a la quinta
        </Link>
      </div>
      <FarmMapLoader mapData={mapResult.data} imagery={imagery} />
    </div>
  );
}
