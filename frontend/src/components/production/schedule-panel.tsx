import Link from "next/link";

import {
  clockInput,
  scheduleStatusLabel,
  weekdayLabels,
  type Occurrence,
  type ScheduleSeries,
} from "@/lib/schedules";

export function ScheduleSection({
  vidrieraId,
  pending,
  loadError,
}: {
  vidrieraId: string;
  pending: Occurrence[] | null;
  loadError?: string;
}) {
  const count = pending?.length ?? 0;
  return (
    <section className="space-y-3" aria-labelledby="programacion-title">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 id="programacion-title" className="text-sm font-semibold">
          Programación
        </h3>
        <div className="flex flex-wrap gap-3">
          <Link
            href={`/produccion/vidrieras/${vidrieraId}/programacion`}
            className="rounded-md border border-line bg-surface px-4 py-2 text-sm font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            Ver programación
          </Link>
          <Link
            href={`/produccion/vidrieras/${vidrieraId}/confirmaciones`}
            className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-strong focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            Confirmar ocurrencias
          </Link>
        </div>
      </div>
      <p className="text-sm leading-6 text-muted">
        La programación muestra lo esperado. El historial muestra solo
        operaciones registradas.
      </p>
      {loadError ? <p role="alert">{loadError}</p> : null}
      {pending && count === 0 ? (
        <p className="text-sm text-muted">
          No hay confirmaciones pendientes en los últimos 14 días.
        </p>
      ) : null}
      {pending && count > 0 ? (
        <p className="text-sm">
          {count === 1
            ? "Hay 1 ocurrencia pendiente de verificación."
            : `Hay ${count} ocurrencias pendientes de verificación.`}
        </p>
      ) : null}
    </section>
  );
}

export function ScheduleList({ schedules }: { schedules: ScheduleSeries[] }) {
  if (schedules.length === 0) {
    return (
      <p className="text-sm text-muted">
        Todavía no hay programación de iluminación ni de nylon negro.
      </p>
    );
  }
  return (
    <ul className="divide-y divide-line rounded-lg border border-line bg-surface">
      {schedules.map((schedule) => {
        const current = schedule.current;
        return (
          <li key={schedule.series_id}>
            <Link
              href={`/produccion/programacion/${schedule.series_id}`}
              className="block space-y-1 px-5 py-3 text-sm hover:bg-background focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
            >
              <span className="font-medium">{current.operation_label}</span>
              <span className="block text-muted">
                {scheduleStatusLabel(current.status)} ·{" "}
                {current.effective_start} – {current.effective_end} ·{" "}
                {clockInput(current.start_time)}–{clockInput(current.end_time)}
              </span>
              <span className="block text-muted">
                {weekdayLabels(current.weekdays)}
                {current.generates ? "" : " · No genera ocurrencias"}
              </span>
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
