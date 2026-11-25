import Link from "next/link";

import { ScheduleCreateForm } from "@/app/produccion/schedule-forms";
import { readJson } from "@/lib/backend";
import { addDays, civilToday } from "@/lib/schedules";
import type { VidrieraDetail } from "@/lib/production";

export const dynamic = "force-dynamic";

export default async function NuevaProgramacionPage({
  params,
}: {
  params: Promise<{ vidrieraId: string }>;
}) {
  const { vidrieraId } = await params;
  const vidriera = await readJson<VidrieraDetail>(
    `/api/production/vidrieras/${vidrieraId}`,
  );
  if (!vidriera.ok) {
    return <p role="alert">{vidriera.message}</p>;
  }
  const today = civilToday();
  return (
    <div className="max-w-3xl space-y-6">
      <Link
        href={`/produccion/vidrieras/${vidrieraId}/programacion`}
        className="text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
      >
        Volver a la programación
      </Link>
      <h2 className="text-2xl font-semibold">Nueva programación</h2>
      <p className="max-w-xl text-sm leading-6 text-muted">
        Define el horario previsto de iluminación artificial o de nylon negro.
        No enciende equipos ni confirma que el trabajo se haya hecho.
      </p>
      <ScheduleCreateForm
        vidrieraId={vidrieraId}
        defaultStart={today}
        defaultEnd={addDays(today, 14)}
      />
    </div>
  );
}
