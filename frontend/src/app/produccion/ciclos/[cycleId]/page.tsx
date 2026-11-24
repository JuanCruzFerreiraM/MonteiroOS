import Link from "next/link";

import {
  CorrectCycleForm,
  FinalizeCycleForm,
} from "@/app/produccion/cycle-forms";
import { readJson } from "@/lib/backend";
import {
  cycleStatusLabel,
  formatCycleDate,
  suggestedClosingDate,
  type CultivationCycle,
} from "@/lib/cycles";
import type { VidrieraDetail } from "@/lib/production";

export const dynamic = "force-dynamic";

export default async function CycleDetailPage({
  params,
}: {
  params: Promise<{ cycleId: string }>;
}) {
  const { cycleId } = await params;
  const cycle = await readJson<CultivationCycle>(
    `/api/production/cycles/${cycleId}`,
  );
  if (!cycle.ok) {
    return <p role="alert">{cycle.message}</p>;
  }
  const record = cycle.data;
  const vidriera = await readJson<VidrieraDetail>(
    `/api/production/vidrieras/${record.vidriera_id}`,
  );
  const backLabel = vidriera.ok
    ? `Volver a ${vidriera.data.code}`
    : "Volver a la vidriera";

  return (
    <div className="max-w-3xl space-y-6">
      <Link
        href={`/produccion/vidrieras/${record.vidriera_id}`}
        className="text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
      >
        {backLabel}
      </Link>
      <header className="space-y-2">
        <p className="text-sm text-muted">Ciclo de cultivo</p>
        <h2 className="text-2xl font-semibold">
          {cycleStatusLabel(record.status)}
        </h2>
      </header>
      <dl className="grid max-w-xl grid-cols-[8rem_1fr] gap-y-2 text-sm">
        <dt className="text-muted">Plantación</dt>
        <dd>{formatCycleDate(record.start_date)}</dd>
        <dt className="text-muted">Cierre</dt>
        <dd>
          {record.end_date
            ? formatCycleDate(record.end_date)
            : "Todavía no está finalizado."}
        </dd>
        <dt className="text-muted">Notas</dt>
        <dd>{record.notes ?? "Sin notas."}</dd>
      </dl>
      {record.status === "active" ? (
        <FinalizeCycleForm
          cycleId={record.id}
          vidrieraId={record.vidriera_id}
          startDate={record.start_date}
          suggestedEndDate={suggestedClosingDate()}
        />
      ) : null}
      <section className="space-y-3" aria-labelledby="correccion-title">
        <h3 id="correccion-title" className="text-sm font-semibold">
          Corregir fechas o notas
        </h3>
        <CorrectCycleForm cycle={record} />
      </section>
    </div>
  );
}
