import Link from "next/link";

import { CanteroEditForm } from "@/app/produccion/forms";
import { readJson } from "@/lib/backend";
import type { VidrieraDetail } from "@/lib/production";

export const dynamic = "force-dynamic";

export default async function EditarCanteroPage({
  params,
  searchParams,
}: {
  params: Promise<{ canteroId: string }>;
  searchParams: Promise<{ vidriera?: string }>;
}) {
  const { canteroId } = await params;
  const query = await searchParams;
  const vidrieraId = query.vidriera;
  if (!vidrieraId) {
    return <p role="alert">Falta la vidriera del cantero.</p>;
  }
  const vidriera = await readJson<VidrieraDetail>(
    `/api/production/vidrieras/${vidrieraId}`,
  );
  if (!vidriera.ok) {
    return <p role="alert">{vidriera.message}</p>;
  }
  const cantero = vidriera.data.canteros.find((item) => item.id === canteroId);
  if (!cantero) {
    return <p role="alert">No se encontró el cantero.</p>;
  }

  return (
    <div className="space-y-6">
      <Link
        href={`/produccion/vidrieras/${vidrieraId}`}
        className="text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
      >
        Volver a {vidriera.data.code}
      </Link>
      <h2 className="text-2xl font-semibold">Editar C{cantero.number}</h2>
      <p className="text-sm text-muted">{cantero.display_code}</p>
      <CanteroEditForm
        id={cantero.id}
        vidrieraId={vidrieraId}
        name={cantero.name}
        active={cantero.active}
      />
    </div>
  );
}
