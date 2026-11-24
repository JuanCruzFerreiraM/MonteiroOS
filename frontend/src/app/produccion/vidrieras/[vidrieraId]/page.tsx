import Link from "next/link";

import { ActiveToggleForm } from "@/app/produccion/forms";
import { CycleSection } from "@/components/production/cycle-panel";
import {
  CanteroList,
  StatusBadge,
} from "@/components/production/production-views";
import { readJson } from "@/lib/backend";
import { suggestedClosingDate, type CycleCollection } from "@/lib/cycles";
import type { VidrieraDetail } from "@/lib/production";

export const dynamic = "force-dynamic";

export default async function VidrieraDetailPage({
  params,
}: {
  params: Promise<{ vidrieraId: string }>;
}) {
  const { vidrieraId } = await params;
  const [vidriera, cycles] = await Promise.all([
    readJson<VidrieraDetail>(`/api/production/vidrieras/${vidrieraId}`),
    readJson<CycleCollection>(`/api/production/vidrieras/${vidrieraId}/cycles`),
  ]);
  if (!vidriera.ok) {
    return <p role="alert">{vidriera.message}</p>;
  }
  const record = vidriera.data;

  return (
    <div className="max-w-3xl space-y-6">
      <Link
        href={`/produccion/quintas/${record.quinta_id}`}
        className="text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
      >
        {record.quinta_name} · {record.quinta_code}
      </Link>
      <header className="space-y-2">
        <p className="text-sm text-muted">{record.code}</p>
        <div className="flex items-center gap-3">
          <h2 className="text-2xl font-semibold">{record.name}</h2>
          <StatusBadge active={record.active} />
        </div>
        {record.notes ? (
          <p className="text-sm leading-6">{record.notes}</p>
        ) : (
          <p className="text-sm text-muted">Sin notas.</p>
        )}
      </header>
      <div className="flex flex-wrap gap-3">
        <Link
          href={`/produccion/vidrieras/${record.id}/editar`}
          className="rounded-md border border-line bg-surface px-4 py-2 text-sm font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Editar datos
        </Link>
        <ActiveToggleForm
          id={record.id}
          active={record.active}
          kind="vidriera"
        />
      </div>
      <section className="space-y-3" aria-labelledby="canteros-title">
        <h3 id="canteros-title" className="text-sm font-semibold">
          Canteros
        </h3>
        <CanteroList vidrieraId={record.id} canteros={record.canteros} />
      </section>
      <CycleSection
        vidrieraId={record.id}
        cycles={cycles.ok ? cycles.data : null}
        loadError={cycles.ok ? undefined : cycles.message}
        suggestedEndDate={suggestedClosingDate()}
      />
    </div>
  );
}
