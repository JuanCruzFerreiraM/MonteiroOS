import Link from "next/link";

import {
  OPERATION_TYPES,
  formatOccurredAt,
  historySearch,
  operationLabel,
  originLabel,
  type Operation,
} from "@/lib/operations";

const fieldClass = "rounded-md border border-line bg-surface px-3 py-2 text-sm";

export function OperationSection({
  vidrieraId,
  operations,
  cycleLabels = {},
  loadError,
}: {
  vidrieraId: string;
  operations: Operation[] | null;
  cycleLabels?: Record<string, string>;
  loadError?: string;
}) {
  return (
    <section className="space-y-3" aria-labelledby="historial-title">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 id="historial-title" className="text-sm font-semibold">
          Historial de producción
        </h3>
        <div className="flex flex-wrap gap-3">
          <Link
            href={`/produccion/vidrieras/${vidrieraId}/historial`}
            className="rounded-md border border-line bg-surface px-4 py-2 text-sm font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            Ver historial
          </Link>
          <Link
            href={`/produccion/vidrieras/${vidrieraId}/operaciones/nueva`}
            className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-strong focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            Registrar operación
          </Link>
        </div>
      </div>
      <p className="text-sm leading-6 text-muted">
        Operaciones registradas, de la más reciente a la más antigua. Lo
        programado y lo no realizado se revisan en Confirmaciones.
      </p>
      {loadError ? <p role="alert">{loadError}</p> : null}
      {operations ? (
        <OperationHistory
          operations={operations}
          cycleLabels={cycleLabels}
          emptyMessage="Todavía no hay operaciones. Registre la primera desde esta vidriera."
        />
      ) : null}
    </section>
  );
}

export function OperationHistory({
  operations,
  cycleLabels = {},
  emptyMessage = "Todavía no hay operaciones.",
}: {
  operations: Operation[];
  cycleLabels?: Record<string, string>;
  emptyMessage?: string;
}) {
  if (operations.length === 0) {
    return <p className="text-sm text-muted">{emptyMessage}</p>;
  }
  return (
    <ul className="divide-y divide-line rounded-lg border border-line bg-surface">
      {operations.map((operation) => (
        <li key={operation.id}>
          <Link
            href={`/produccion/operaciones/${operation.id}`}
            className="block space-y-1 px-5 py-3 text-sm hover:bg-background focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            <span className="flex items-baseline justify-between gap-4">
              <span className="font-medium">{operation.operation_label}</span>
              <span className="text-muted">
                {formatOccurredAt(operation.occurred_at)}
              </span>
            </span>
            <span className="block text-muted">
              {originLabel(operation.origin)} ·{" "}
              {cycleText(operation, cycleLabels)}
            </span>
            {operation.interval_start && operation.interval_end ? (
              <span className="block text-muted">
                Intervalo real: {formatOccurredAt(operation.interval_start)} –{" "}
                {formatOccurredAt(operation.interval_end)}
              </span>
            ) : null}
            {operation.notes ? (
              <span className="block">{operation.notes}</span>
            ) : null}
          </Link>
        </li>
      ))}
    </ul>
  );
}

export function HistoryFilters({
  vidrieraId,
  type = "",
  from = "",
  to = "",
  cycle = "",
  cycles,
}: {
  vidrieraId: string;
  type?: string;
  from?: string;
  to?: string;
  cycle?: string;
  cycles: { id: string; label: string }[];
}) {
  const filtered = Boolean(type || from || to || cycle);
  return (
    <form
      className="flex flex-wrap items-end gap-3"
      method="get"
      action={`/produccion/vidrieras/${vidrieraId}/historial`}
    >
      <label className="space-y-1 text-sm">
        <span className="block font-medium">Desde</span>
        <input
          type="date"
          name="from"
          defaultValue={from}
          className={fieldClass}
        />
      </label>
      <label className="space-y-1 text-sm">
        <span className="block font-medium">Hasta</span>
        <input type="date" name="to" defaultValue={to} className={fieldClass} />
      </label>
      <label className="space-y-1 text-sm">
        <span className="block font-medium">Tipo</span>
        <select name="type" defaultValue={type} className={fieldClass}>
          <option value="">Todos los tipos</option>
          {OPERATION_TYPES.map((item) => (
            <option key={item} value={item}>
              {operationLabel(item)}
            </option>
          ))}
        </select>
      </label>
      <label className="space-y-1 text-sm">
        <span className="block font-medium">Ciclo</span>
        <select name="cycle" defaultValue={cycle} className={fieldClass}>
          <option value="">Todos los ciclos</option>
          <option value="none">Sin ciclo</option>
          {cycles.map((item) => (
            <option key={item.id} value={item.id}>
              {item.label}
            </option>
          ))}
        </select>
      </label>
      <button
        type="submit"
        className="rounded-md border border-line bg-surface px-4 py-2 text-sm font-medium"
      >
        Filtrar
      </button>
      {filtered ? (
        <Link
          href={`/produccion/vidrieras/${vidrieraId}/historial`}
          className="px-2 py-2 text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
        >
          Restablecer
        </Link>
      ) : null}
    </form>
  );
}

export function historyPageHref(
  vidrieraId: string,
  query: {
    type?: string;
    from?: string;
    to?: string;
    cycle?: string;
    cursor?: string;
  },
): string {
  return `/produccion/vidrieras/${vidrieraId}/historial${historySearch(query)}`;
}

function cycleText(
  operation: Operation,
  cycleLabels: Record<string, string>,
): string {
  if (!operation.cycle_id) {
    return "Sin ciclo";
  }
  return cycleLabels[operation.cycle_id] ?? "Vinculado a un ciclo";
}
