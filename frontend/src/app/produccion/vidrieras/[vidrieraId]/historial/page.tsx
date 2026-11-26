import Link from "next/link";

import {
  HistoryFilters,
  OperationHistory,
  historyPageHref,
} from "@/components/production/operation-panel";
import { readJson } from "@/lib/backend";
import {
  cycleLabelMap,
  cycleOptionLabel,
  type CycleCollection,
} from "@/lib/cycles";
import type { OperationPage } from "@/lib/operations";
import type { VidrieraDetail } from "@/lib/production";

export const dynamic = "force-dynamic";

export default async function HistoryPage({
  params,
  searchParams,
}: {
  params: Promise<{ vidrieraId: string }>;
  searchParams: Promise<{
    from?: string;
    to?: string;
    type?: string;
    cycle?: string;
    cursor?: string;
  }>;
}) {
  const { vidrieraId } = await params;
  const query = await searchParams;
  const type = query.type ?? "";
  const from = query.from ?? "";
  const to = query.to ?? "";
  const cycle = query.cycle ?? "";
  const cursor = query.cursor ?? "";
  const vidriera = await readJson<VidrieraDetail>(
    `/api/production/vidrieras/${vidrieraId}`,
  );
  if (!vidriera.ok) {
    return <p role="alert">{vidriera.message}</p>;
  }
  const cycles = await readJson<CycleCollection>(
    `/api/production/vidrieras/${vidrieraId}/cycles`,
  );
  const parameters = new URLSearchParams({ limit: "20" });
  if (type) {
    parameters.set("operation_type", type);
  }
  if (from) {
    parameters.set("from", from);
  }
  if (to) {
    parameters.set("to", to);
  }
  if (cycle) {
    parameters.set("cycle", cycle);
  }
  if (cursor) {
    parameters.set("cursor", cursor);
  }
  const page = await readJson<OperationPage>(
    `/api/operations/vidrieras/${vidrieraId}/operations?${parameters}`,
  );
  const labels = cycles.ok ? cycleLabelMap(cycles.data) : {};
  const choices = cycles.ok
    ? [
        ...(cycles.data.active
          ? [
              {
                id: cycles.data.active.id,
                label: cycleOptionLabel(cycles.data.active),
              },
            ]
          : []),
        ...cycles.data.history.map((item) => ({
          id: item.id,
          label: cycleOptionLabel(item),
        })),
      ]
    : [];
  const filtered = Boolean(type || from || to || cycle);
  const emptyMessage = cursor
    ? "No hay operaciones más antiguas."
    : filtered
      ? "Ninguna operación coincide con el filtro."
      : "Todavía no hay operaciones. Registre la primera desde esta vidriera.";

  return (
    <div className="max-w-3xl space-y-6">
      <Link
        href={`/produccion/vidrieras/${vidrieraId}`}
        className="text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
      >
        Volver a {vidriera.data.code}
      </Link>
      <header className="space-y-2">
        <h2 className="text-2xl font-semibold">Historial de producción</h2>
        <p className="max-w-3xl text-sm leading-6 text-muted">
          Solo operaciones registradas. Una ocurrencia programada, pendiente o
          marcada como no realizada no aparece acá.
        </p>
      </header>
      <HistoryFilters
        vidrieraId={vidrieraId}
        type={type}
        from={from}
        to={to}
        cycle={cycle}
        cycles={choices}
      />
      <p className="text-sm">
        <Link
          href={`/produccion/vidrieras/${vidrieraId}/confirmaciones`}
          className="font-medium text-accent-strong underline-offset-2 hover:underline"
        >
          Ir a confirmaciones
        </Link>
      </p>
      {page.ok ? (
        <OperationHistory
          operations={page.data.items}
          cycleLabels={labels}
          emptyMessage={emptyMessage}
        />
      ) : (
        <p role="alert">{page.message}</p>
      )}
      {page.ok && page.data.next_cursor ? (
        <Link
          href={historyPageHref(vidrieraId, {
            type,
            from,
            to,
            cycle,
            cursor: page.data.next_cursor,
          })}
          className="inline-block rounded-md border border-line bg-surface px-4 py-2 text-sm font-medium"
        >
          Ver más antiguas
        </Link>
      ) : null}
      {cursor ? (
        <Link
          href={historyPageHref(vidrieraId, { type, from, to, cycle })}
          className="block text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
        >
          Volver al principio
        </Link>
      ) : null}
    </div>
  );
}
