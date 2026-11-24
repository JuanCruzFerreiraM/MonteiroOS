import Link from "next/link";

import { OperationEditForm } from "@/app/produccion/operation-forms";
import { readJson } from "@/lib/backend";
import type { CycleCollection } from "@/lib/cycles";
import { formatCycleDate } from "@/lib/cycles";
import {
  formatOccurredAt,
  timingBasisLabel,
  type Operation,
} from "@/lib/operations";

export const dynamic = "force-dynamic";

export default async function OperationDetailPage({
  params,
}: {
  params: Promise<{ operationId: string }>;
}) {
  const { operationId } = await params;
  const operation = await readJson<Operation>(
    `/api/operations/operations/${operationId}`,
  );
  if (!operation.ok) {
    return <p role="alert">{operation.message}</p>;
  }
  const record = operation.data;
  const cycles = await readJson<CycleCollection>(
    `/api/production/vidrieras/${record.vidriera_id}/cycles`,
  );
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
  const basis = timingBasisLabel(record.timing_basis);

  return (
    <div className="max-w-3xl space-y-6">
      <Link
        href={`/produccion/vidrieras/${record.vidriera_id}`}
        className="text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
      >
        Volver a la vidriera
      </Link>
      <header className="space-y-2">
        <p className="text-sm text-muted">
          {record.origin === "scheduled"
            ? "Confirmada desde la programación"
            : "Registro manual"}
        </p>
        <h2 className="text-2xl font-semibold">{record.operation_label}</h2>
      </header>
      <dl className="grid max-w-xl grid-cols-[8rem_1fr] gap-y-2 text-sm">
        <dt className="text-muted">Momento</dt>
        <dd>{formatOccurredAt(record.occurred_at)}</dd>
        <dt className="text-muted">Ciclo</dt>
        <dd>{record.cycle_id ? "Vinculado a un ciclo" : "Sin ciclo"}</dd>
        <dt className="text-muted">Notas</dt>
        <dd>{record.notes ?? "Sin notas."}</dd>
        {record.interval_start && record.interval_end ? (
          <>
            <dt className="text-muted">Intervalo</dt>
            <dd>
              {formatOccurredAt(record.interval_start)} –{" "}
              {formatOccurredAt(record.interval_end)}
            </dd>
          </>
        ) : null}
      </dl>
      {basis ? <p className="text-sm leading-6 text-muted">{basis}</p> : null}
      {record.resolution_id ? (
        <p className="text-sm leading-6 text-muted">
          El intervalo de esta ficha es el horario real confirmado. Corregirlo
          no cambia el horario que estaba programado.
        </p>
      ) : null}
      <section className="space-y-3" aria-labelledby="correccion-operacion">
        <h3 id="correccion-operacion" className="text-sm font-semibold">
          Corregir
        </h3>
        <OperationEditForm operation={record} cycles={choices} />
      </section>
    </div>
  );
}
