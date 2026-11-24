import Link from "next/link";

import {
  ScheduleLifecycleForms,
  ScheduleReviseForm,
} from "@/app/produccion/schedule-forms";
import { readJson } from "@/lib/backend";
import {
  addDays,
  civilToday,
  clockInput,
  scheduleStatusLabel,
  weekdayLabels,
  type ScheduleSeries,
} from "@/lib/schedules";

export const dynamic = "force-dynamic";

export default async function ScheduleDetailPage({
  params,
}: {
  params: Promise<{ seriesId: string }>;
}) {
  const { seriesId } = await params;
  const schedule = await readJson<ScheduleSeries>(
    `/api/operations/schedules/${seriesId}`,
  );
  if (!schedule.ok) {
    return <p role="alert">{schedule.message}</p>;
  }
  const current = schedule.data.current;
  const tomorrow = addDays(civilToday(), 1);
  return (
    <div className="max-w-3xl space-y-6">
      <Link
        href={`/produccion/vidrieras/${current.vidriera_id}/programacion`}
        className="text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
      >
        Volver a la programación
      </Link>
      <header className="space-y-2">
        <p className="text-sm text-muted">
          {scheduleStatusLabel(current.status)}
        </p>
        <h2 className="text-2xl font-semibold">{current.operation_label}</h2>
        <p className="text-sm text-muted">
          {current.effective_start} – {current.effective_end} ·{" "}
          {clockInput(current.start_time)}–{clockInput(current.end_time)} ·{" "}
          {weekdayLabels(current.weekdays)}
        </p>
      </header>
      <section className="space-y-3" aria-labelledby="revisiones">
        <h3 id="revisiones" className="text-sm font-semibold">
          Revisiones
        </h3>
        <ul className="divide-y divide-line rounded-lg border border-line bg-surface text-sm">
          {schedule.data.revisions.map((revision) => (
            <li key={revision.id} className="px-5 py-3">
              {revision.effective_start} – {revision.effective_end} ·{" "}
              {clockInput(revision.start_time)}–{clockInput(revision.end_time)}{" "}
              · {scheduleStatusLabel(revision.status)}
              {revision.generates ? "" : " · Sin ocurrencias"}
            </li>
          ))}
        </ul>
      </section>
      {current.status === "ended" ? (
        <p className="text-sm text-muted">Esta programación ya finalizó.</p>
      ) : (
        <section className="space-y-3" aria-labelledby="cambio-programacion">
          <h3 id="cambio-programacion" className="text-sm font-semibold">
            Cambiar desde una fecha
          </h3>
          <ScheduleReviseForm revision={current} defaultFrom={tomorrow} />
          <ScheduleLifecycleForms revision={current} defaultFrom={tomorrow} />
        </section>
      )}
    </div>
  );
}
