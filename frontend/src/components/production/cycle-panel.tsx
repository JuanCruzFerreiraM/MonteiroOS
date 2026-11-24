import Link from "next/link";

import {
  FinalizeCycleForm,
  StartCycleForm,
} from "@/app/produccion/cycle-forms";
import {
  cycleStatusLabel,
  formatCycleDate,
  type CycleCollection,
} from "@/lib/cycles";

import { EmptyState } from "./production-views";

export function CycleSection({
  vidrieraId,
  cycles,
  loadError,
  suggestedEndDate,
}: {
  vidrieraId: string;
  cycles: CycleCollection | null;
  loadError?: string;
  suggestedEndDate: string;
}) {
  return (
    <section className="space-y-4" aria-labelledby="ciclos-title">
      <h3 id="ciclos-title" className="text-sm font-semibold">
        Ciclo de cultivo
      </h3>
      {loadError ? <p role="alert">{loadError}</p> : null}
      {cycles ? (
        <CycleBody
          vidrieraId={vidrieraId}
          cycles={cycles}
          suggestedEndDate={suggestedEndDate}
        />
      ) : null}
    </section>
  );
}

function CycleBody({
  vidrieraId,
  cycles,
  suggestedEndDate,
}: {
  vidrieraId: string;
  cycles: CycleCollection;
  suggestedEndDate: string;
}) {
  const active = cycles.active;
  return (
    <>
      {active ? (
        <div className="space-y-4 rounded-lg border border-line bg-surface px-5 py-4">
          <dl className="grid grid-cols-[8rem_1fr] gap-y-2 text-sm">
            <dt className="text-muted">Estado</dt>
            <dd>{cycleStatusLabel(active.status)}</dd>
            <dt className="text-muted">Plantación</dt>
            <dd>{formatCycleDate(active.start_date)}</dd>
            <dt className="text-muted">Notas</dt>
            <dd>{active.notes ?? "Sin notas."}</dd>
          </dl>
          <Link
            href={`/produccion/ciclos/${active.id}`}
            className="text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
          >
            Corregir fechas o notas
          </Link>
          <FinalizeCycleForm
            cycleId={active.id}
            vidrieraId={vidrieraId}
            startDate={active.start_date}
            suggestedEndDate={suggestedEndDate}
          />
        </div>
      ) : (
        <div className="space-y-4">
          <EmptyState
            title="No hay un ciclo activo"
            body="El ciclo empieza el día real de la plantación. La limpieza, la preparación y el mantenimiento pueden quedar en la vidriera, sin asignarse a un ciclo."
          />
          <StartCycleForm vidrieraId={vidrieraId} />
        </div>
      )}
      <CycleHistory history={cycles.history} />
    </>
  );
}

function CycleHistory({ history }: { history: CycleCollection["history"] }) {
  if (history.length === 0) {
    return (
      <p className="text-sm text-muted">Todavía no hay ciclos finalizados.</p>
    );
  }
  return (
    <div className="space-y-2">
      <h4 className="text-sm font-semibold">Ciclos anteriores</h4>
      <ul className="divide-y divide-line rounded-lg border border-line bg-surface">
        {history.map((cycle) => (
          <li key={cycle.id}>
            <Link
              href={`/produccion/ciclos/${cycle.id}`}
              className="flex items-center justify-between gap-4 px-5 py-3 text-sm hover:bg-background focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
            >
              <span>
                {formatCycleDate(cycle.start_date)} –{" "}
                {formatCycleDate(cycle.end_date ?? "")}
              </span>
              <span className="text-muted">
                {cycleStatusLabel(cycle.status)}
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
