import Link from "next/link";

import { VidrieraCreateForm } from "@/app/produccion/forms";
import { readJson } from "@/lib/backend";
import type { NextVidrieraCode, Quinta } from "@/lib/production";

export const dynamic = "force-dynamic";

export default async function NuevaVidrieraPage({
  params,
}: {
  params: Promise<{ quintaId: string }>;
}) {
  const { quintaId } = await params;
  const quinta = await readJson<Quinta>(`/api/production/quintas/${quintaId}`);
  if (!quinta.ok) {
    return <p role="alert">{quinta.message}</p>;
  }
  if (!quinta.data.active) {
    return (
      <p role="alert">No se puede crear una vidriera en una quinta inactiva.</p>
    );
  }
  const suggestion = await readJson<NextVidrieraCode>(
    `/api/production/quintas/${quintaId}/vidrieras/next-code`,
  );

  return (
    <div className="space-y-6">
      <Link
        href={`/produccion/quintas/${quintaId}`}
        className="text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
      >
        Volver a {quinta.data.name}
      </Link>
      <header className="space-y-1">
        <p className="text-sm text-muted">
          {quinta.data.name} · {quinta.data.code}
        </p>
        <h2 className="text-2xl font-semibold">Nueva vidriera</h2>
      </header>
      {suggestion.ok ? (
        <VidrieraCreateForm
          quintaId={quintaId}
          suggestedCode={suggestion.data.code}
        />
      ) : (
        <p role="alert">{suggestion.message}</p>
      )}
    </div>
  );
}
