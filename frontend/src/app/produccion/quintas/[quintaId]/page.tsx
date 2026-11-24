import { QuintaOverview } from "@/components/production/quinta-overview";
import { readJson } from "@/lib/backend";
import type { Quinta, QuintaMap, Vidriera } from "@/lib/production";

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
  const [quinta, mapResult, vidrieras] = await Promise.all([
    readJson<Quinta>(`/api/production/quintas/${quintaId}`),
    readJson<QuintaMap>(
      `/api/production/quintas/${quintaId}/map?include_inactive=true`,
    ),
    readJson<Vidriera[]>(
      `/api/production/quintas/${quintaId}/vidrieras?include_inactive=${
        includeInactive ? "true" : "false"
      }`,
    ),
  ]);
  if (!quinta.ok) {
    return <p role="alert">{quinta.message}</p>;
  }

  return (
    <QuintaOverview
      quinta={quinta.data}
      map={mapResult.ok ? mapResult.data : null}
      mapFailed={!mapResult.ok}
      vidrieras={vidrieras.ok ? vidrieras.data : null}
      vidrierasMessage={vidrieras.ok ? null : vidrieras.message}
      includeInactive={includeInactive}
    />
  );
}
