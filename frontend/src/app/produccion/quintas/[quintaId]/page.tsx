import Link from "next/link";

import { ActiveToggleForm } from "@/app/produccion/forms";
import {
  StatusBadge,
  VidrieraList,
} from "@/components/production/production-views";
import { readJson } from "@/lib/backend";
import type { Quinta, Vidriera } from "@/lib/production";

export const dynamic = "force-dynamic";

export default async function QuintaDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ quintaId: string }>;
  searchParams: Promise<{ incluir_inactivas?: string }>;
}) {
  const { quintaId } = await params;
  const query = await searchParams;
  const includeInactive = query.incluir_inactivas === "1";
  const quinta = await readJson<Quinta>(`/api/production/quintas/${quintaId}`);
  if (!quinta.ok) {
    return <p role="alert">{quinta.message}</p>;
  }
  const vidrieras = await readJson<Vidriera[]>(
    `/api/production/quintas/${quintaId}/vidrieras?include_inactive=${
      includeInactive ? "true" : "false"
    }`,
  );

  return (
    <div className="max-w-3xl space-y-6">
      <Link
        href="/produccion"
        className="text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
      >
        Volver a producción
      </Link>
      <header className="space-y-2">
        <p className="text-sm text-muted">{quinta.data.code}</p>
        <div className="flex items-center gap-3">
          <h2 className="text-2xl font-semibold">{quinta.data.name}</h2>
          <StatusBadge active={quinta.data.active} />
        </div>
        {quinta.data.notes ? (
          <p className="text-sm leading-6">{quinta.data.notes}</p>
        ) : (
          <p className="text-sm text-muted">Sin notas.</p>
        )}
      </header>
      <div className="flex flex-wrap gap-3">
        <Link
          href={`/produccion/quintas/${quintaId}/editar`}
          className="rounded-md border border-line bg-surface px-4 py-2 text-sm font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Editar datos
        </Link>
        {quinta.data.active ? (
          <Link
            href={`/produccion/quintas/${quintaId}/vidrieras/nueva`}
            className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-strong focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            Crear vidriera
          </Link>
        ) : (
          <p className="text-sm text-muted">
            Active la quinta para crear vidrieras.
          </p>
        )}
      </div>
      <ActiveToggleForm
        id={quinta.data.id}
        active={quinta.data.active}
        kind="quinta"
      />
      {vidrieras.ok ? (
        <VidrieraList
          quintaId={quintaId}
          vidrieras={vidrieras.data}
          allowCreate={quinta.data.active}
        />
      ) : (
        <p role="alert">{vidrieras.message}</p>
      )}
      <Link
        href={
          includeInactive
            ? `/produccion/quintas/${quintaId}`
            : `/produccion/quintas/${quintaId}?incluir_inactivas=1`
        }
        className="inline-block text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
      >
        {includeInactive
          ? "Ocultar vidrieras inactivas"
          : "Ver vidrieras inactivas"}
      </Link>
    </div>
  );
}
