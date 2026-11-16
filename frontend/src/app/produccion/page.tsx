import Link from "next/link";

import { QuintaList } from "@/components/production/production-views";
import { readJson } from "@/lib/backend";
import type { Quinta } from "@/lib/production";

export const dynamic = "force-dynamic";

export default async function ProduccionPage({
  searchParams,
}: {
  searchParams: Promise<{ incluir_inactivas?: string }>;
}) {
  const params = await searchParams;
  const includeInactive = params.incluir_inactivas === "1";
  const result = await readJson<Quinta[]>(
    `/api/production/quintas?include_inactive=${includeInactive ? "true" : "false"}`,
  );

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-center justify-between gap-4">
        <p className="text-sm leading-6 text-muted">
          Quintas, vidrieras y canteros de la producción.
        </p>
        <Link
          href="/produccion/quintas/nueva"
          className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-strong focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Crear quinta
        </Link>
      </div>
      {result.ok ? (
        <QuintaList quintas={result.data} />
      ) : (
        <p role="alert" className="text-sm text-warning">
          {result.message}
        </p>
      )}
      <Link
        href={
          includeInactive ? "/produccion" : "/produccion?incluir_inactivas=1"
        }
        className="inline-block text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
      >
        {includeInactive ? "Ocultar inactivas" : "Ver inactivas"}
      </Link>
    </div>
  );
}
