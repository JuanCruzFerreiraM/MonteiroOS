import Link from "next/link";

import { OccurrenceBoard } from "@/components/production/occurrence-board";
import { readJson } from "@/lib/backend";
import type { CycleCollection } from "@/lib/cycles";
import { formatCycleDate } from "@/lib/cycles";
import { addDays, civilToday, type Occurrence } from "@/lib/schedules";
import type { VidrieraDetail } from "@/lib/production";

export const dynamic = "force-dynamic";

const STATUSES = [
  { value: "", label: "Todos los estados" },
  { value: "scheduled", label: "Programadas" },
  { value: "unverified", label: "Pendientes de verificación" },
  { value: "confirmed", label: "Confirmadas" },
  { value: "not_occurred", label: "No realizadas" },
];

export default async function ConfirmacionesPage({
  params,
  searchParams,
}: {
  params: Promise<{ vidrieraId: string }>;
  searchParams: Promise<{
    from?: string;
    to?: string;
    type?: string;
    status?: string;
  }>;
}) {
  const { vidrieraId } = await params;
  const query = await searchParams;
  const today = civilToday();
  const from = query.from || addDays(today, -7);
  const to = query.to || addDays(today, 7);
  const type = query.type || "";
  const status = query.status || "";
  const vidriera = await readJson<VidrieraDetail>(
    `/api/production/vidrieras/${vidrieraId}`,
  );
  if (!vidriera.ok) {
    return <p role="alert">{vidriera.message}</p>;
  }
  const parameters = new URLSearchParams({ from, to });
  if (type) {
    parameters.set("operation_type", type);
  }
  if (status) {
    parameters.set("status", status);
  }
  const [occurrences, cycles] = await Promise.all([
    readJson<Occurrence[]>(
      `/api/operations/vidrieras/${vidrieraId}/occurrences?${parameters}`,
    ),
    readJson<CycleCollection>(`/api/production/vidrieras/${vidrieraId}/cycles`),
  ]);
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
    <div className="max-w-5xl space-y-6">
      <Link
        href={`/produccion/vidrieras/${vidrieraId}`}
        className="text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
      >
        Volver a {vidriera.data.code}
      </Link>
      <header className="space-y-2">
        <h2 className="text-2xl font-semibold">Confirmar ocurrencias</h2>
        <p className="max-w-3xl text-sm leading-6 text-muted">
          Una ocurrencia programada todavía no ocurrió. Una pendiente espera
          verificación. Confirmar no afirma que un sensor haya medido el
          horario.
        </p>
      </header>
      <form className="flex flex-wrap items-end gap-3" method="get">
        <label className="space-y-1 text-sm">
          <span className="block font-medium">Desde</span>
          <input
            type="date"
            name="from"
            defaultValue={from}
            className="rounded-md border border-line bg-surface px-3 py-2"
          />
        </label>
        <label className="space-y-1 text-sm">
          <span className="block font-medium">Hasta</span>
          <input
            type="date"
            name="to"
            defaultValue={to}
            className="rounded-md border border-line bg-surface px-3 py-2"
          />
        </label>
        <label className="space-y-1 text-sm">
          <span className="block font-medium">Tipo</span>
          <select
            name="type"
            defaultValue={type}
            className="rounded-md border border-line bg-surface px-3 py-2"
          >
            <option value="">Iluminación y nylon</option>
            <option value="artificial_lighting">Iluminación artificial</option>
            <option value="black_nylon">Cobertura con nylon negro</option>
          </select>
        </label>
        <label className="space-y-1 text-sm">
          <span className="block font-medium">Estado</span>
          <select
            name="status"
            defaultValue={status}
            className="rounded-md border border-line bg-surface px-3 py-2"
          >
            {STATUSES.map((item) => (
              <option key={item.value} value={item.value}>
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
      </form>
      {occurrences.ok ? (
        <OccurrenceBoard
          vidrieraId={vidrieraId}
          occurrences={occurrences.data}
          cycles={choices}
        />
      ) : (
        <p role="alert">{occurrences.message}</p>
      )}
    </div>
  );
}
