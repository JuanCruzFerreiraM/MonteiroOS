import Link from "next/link";

import { VidrieraEditForm } from "@/app/produccion/forms";
import { readJson } from "@/lib/backend";
import type { VidrieraDetail } from "@/lib/production";

export const dynamic = "force-dynamic";

export default async function EditarVidrieraPage({
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

  return (
    <div className="space-y-6">
      <Link
        href={`/produccion/vidrieras/${vidrieraId}`}
        className="text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
      >
        Volver a {vidriera.data.code}
      </Link>
      <h2 className="text-2xl font-semibold">Editar {vidriera.data.name}</h2>
      <p className="text-sm text-muted">
        El código {vidriera.data.code} y la quinta {vidriera.data.quinta_code}{" "}
        permanecen iguales.
      </p>
      <VidrieraEditForm
        id={vidriera.data.id}
        name={vidriera.data.name}
        notes={vidriera.data.notes}
      />
    </div>
  );
}
