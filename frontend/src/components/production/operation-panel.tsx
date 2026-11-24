import Link from "next/link";

import { formatOccurredAt, type Operation } from "@/lib/operations";

export function OperationSection({
  vidrieraId,
  operations,
  loadError,
}: {
  vidrieraId: string;
  operations: Operation[] | null;
  loadError?: string;
}) {
  return (
    <section className="space-y-3" aria-labelledby="operaciones-title">
      <div className="flex items-center justify-between gap-4">
        <h3 id="operaciones-title" className="text-sm font-semibold">
          Operaciones
        </h3>
        <Link
          href={`/produccion/vidrieras/${vidrieraId}/operaciones/nueva`}
          className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-strong focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Registrar operación
        </Link>
      </div>
      {loadError ? <p role="alert">{loadError}</p> : null}
      {operations && operations.length === 0 ? (
        <p className="text-sm text-muted">Todavía no hay operaciones.</p>
      ) : null}
      {operations && operations.length > 0 ? (
        <ul className="divide-y divide-line rounded-lg border border-line bg-surface">
          {operations.map((operation) => (
            <li key={operation.id}>
              <Link
                href={`/produccion/operaciones/${operation.id}`}
                className="flex items-center justify-between gap-4 px-5 py-3 text-sm hover:bg-background focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
              >
                <span>
                  {operation.operation_label}
                  {operation.cycle_id ? "" : " · Sin ciclo"}
                </span>
                <span className="text-muted">
                  {formatOccurredAt(operation.occurred_at)}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}
