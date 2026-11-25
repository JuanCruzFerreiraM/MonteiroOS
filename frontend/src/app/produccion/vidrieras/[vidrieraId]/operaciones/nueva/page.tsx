import Link from "next/link";

import { OperationCreateForm } from "@/app/produccion/operation-forms";
import { readJson } from "@/lib/backend";
import type { CycleCollection } from "@/lib/cycles";
import { formatCycleDate } from "@/lib/cycles";
import type { VidrieraDetail } from "@/lib/production";

export const dynamic = "force-dynamic";

export default async function NuevaOperacionPage({
  params,
}: {
  params: Promise<{ vidrieraId: string }>;
}) {
  const { vidrieraId } = await params;
  const [vidriera, cycles] = await Promise.all([
    readJson<VidrieraDetail>(`/api/production/vidrieras/${vidrieraId}`),
    readJson<CycleCollection>(`/api/production/vidrieras/${vidrieraId}/cycles`),
  ]);
  if (!vidriera.ok) {
    return <p role="alert">{vidriera.message}</p>;
  }
  const choices = cycles.ok
    ? [
        ...(cycles.data.active
          ? [
              {
                id: cycles.data.active.id,
                label: `Activo · ${formatCycleDate(cycles.data.active.start_date)}`,
              },
            ]
          : []),
        ...cycles.data.history.map((cycle) => ({
          id: cycle.id,
          label: `Finalizado · ${formatCycleDate(cycle.start_date)} – ${formatCycleDate(cycle.end_date ?? "")}`,
        })),
      ]
    : [];

  return (
    <div className="max-w-3xl space-y-6">
      <Link
        href={`/produccion/vidrieras/${vidrieraId}`}
        className="text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
      >
        Volver a {vidriera.data.code}
      </Link>
      <h2 className="text-2xl font-semibold">Registrar operación</h2>
      {cycles.ok ? null : <p role="alert">{cycles.message}</p>}
      <OperationCreateForm
        vidrieraId={vidrieraId}
        cycles={choices}
        defaultCycleId={cycles.ok ? (cycles.data.active?.id ?? null) : null}
      />
    </div>
  );
}
