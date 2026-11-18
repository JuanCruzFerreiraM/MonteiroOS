import Link from "next/link";

import { QuintaEditForm } from "@/app/produccion/forms";
import { readJson } from "@/lib/backend";
import type { Quinta } from "@/lib/production";

export const dynamic = "force-dynamic";

export default async function EditarQuintaPage({
  params,
}: {
  params: Promise<{ quintaId: string }>;
}) {
  const { quintaId } = await params;
  const quinta = await readJson<Quinta>(`/api/production/quintas/${quintaId}`);
  if (!quinta.ok) {
    return <p role="alert">{quinta.message}</p>;
  }

  return (
    <div className="space-y-6">
      <Link
        href={`/produccion/quintas/${quintaId}`}
        className="text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
      >
        Volver a {quinta.data.code}
      </Link>
      <h2 className="text-2xl font-semibold">Editar {quinta.data.name}</h2>
      <p className="text-sm text-muted">
        El código {quinta.data.code} permanece igual.
      </p>
      <QuintaEditForm
        id={quinta.data.id}
        name={quinta.data.name}
        notes={quinta.data.notes}
      />
    </div>
  );
}
