import Link from "next/link";

import { ScheduleList } from "@/components/production/schedule-panel";
import { readJson } from "@/lib/backend";
import type { ScheduleSeries } from "@/lib/schedules";
import type { VidrieraDetail } from "@/lib/production";

export const dynamic = "force-dynamic";

export default async function ProgramacionPage({
  params,
}: {
  params: Promise<{ vidrieraId: string }>;
}) {
  const { vidrieraId } = await params;
  const [vidriera, schedules] = await Promise.all([
    readJson<VidrieraDetail>(`/api/production/vidrieras/${vidrieraId}`),
    readJson<ScheduleSeries[]>(
      `/api/operations/vidrieras/${vidrieraId}/schedules`,
    ),
  ]);
  if (!vidriera.ok) {
    return <p role="alert">{vidriera.message}</p>;
  }
  return (
    <div className="max-w-3xl space-y-6">
      <Link
        href={`/produccion/vidrieras/${vidrieraId}`}
        className="text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
      >
        Volver a {vidriera.data.code}
      </Link>
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-2xl font-semibold">Programación</h2>
        <Link
          href={`/produccion/vidrieras/${vidrieraId}/programacion/nueva`}
          className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-strong focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Nueva programación
        </Link>
      </div>
      {schedules.ok ? (
        <ScheduleList schedules={schedules.data} />
      ) : (
        <p role="alert">{schedules.message}</p>
      )}
    </div>
  );
}
