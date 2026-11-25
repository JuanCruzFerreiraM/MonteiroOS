import Link from "next/link";

import {
  CorrectCycleForm,
  FinalizeCycleForm,
} from "@/app/produccion/cycle-forms";
import { OperationHistory } from "@/components/production/operation-panel";
import { readJson } from "@/lib/backend";
import {
  cycleStatusLabel,
  formatCycleDate,
  suggestedClosingDate,
  type CultivationCycle,
} from "@/lib/cycles";
import type { OperationPage } from "@/lib/operations";
import type { VidrieraDetail } from "@/lib/production";

export const dynamic = "force-dynamic";

export default async function CycleDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ cycleId: string }>;
  searchParams: Promise<{ cursor?: string }>;
}) {
  const { cycleId } = await params;
  const query = await searchParams;
  const cycle = await readJson<CultivationCycle>(
    `/api/production/cycles/${cycleId}`,
  );
  if (!cycle.ok) {
    return <p role="alert">{cycle.message}</p>;
  }
  const record = cycle.data;
  const cursor = query.cursor ?? "";
  const historyParameters = new URLSearchParams({
    cycle: record.id,
    limit: "20",
  });
  if (cursor) {
    historyParameters.set("cursor", cursor);
  }
  const [vidriera, history] = await Promise.all([
    readJson<VidrieraDetail>(`/api/production/vidrieras/${record.vidriera_id}`),
    readJson<OperationPage>(
      `/api/operations/vidrieras/${record.vidriera_id}/operations?${historyParameters}`,
    ),
  ]);
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
      <section className="space-y-3" aria-labelledby="historial-ciclo">
        <h3 id="historial-ciclo" className="text-sm font-semibold">
          Operaciones de este ciclo
        </h3>
        <p className="text-sm leading-6 text-muted">
          Solo las operaciones guardadas con este ciclo. Una operación sin ciclo
          no aparece acá.
        </p>
        {history.ok ? (
          <OperationHistory
            operations={history.data.items}
            cycleLabels={{ [record.id]: "Este ciclo" }}
            emptyMessage="Este ciclo no tiene operaciones asociadas."
          />
        ) : (
          <p role="alert">{history.message}</p>
        )}
        {history.ok && history.data.next_cursor ? (
          <Link
            href={`/produccion/ciclos/${record.id}?cursor=${encodeURIComponent(history.data.next_cursor)}`}
            className="inline-block rounded-md border border-line bg-surface px-4 py-2 text-sm font-medium"
          >
            Ver más antiguas
          </Link>
        ) : null}
      </section>
      <section className="space-y-3" aria-labelledby="correccion-title">
        <h3 id="correccion-title" className="text-sm font-semibold">
          Corregir fechas o notas
        </h3>
        <CorrectCycleForm cycle={record} />
      </section>
    </div>
  );
}
