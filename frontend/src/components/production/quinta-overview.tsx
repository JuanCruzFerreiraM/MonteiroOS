import Link from "next/link";

import { ActiveToggleForm } from "@/app/produccion/forms";
import { FarmOverviewLoader } from "@/components/map/farm-overview-loader";
import {
  EmptyState,
  StatusBadge,
  VidrieraList,
} from "@/components/production/production-views";
import { polygonsForOverview } from "@/lib/map-interaction";
import type { Quinta, QuintaMap, Vidriera } from "@/lib/production";

export function QuintaOverview({
  quinta,
  map,
  mapFailed,
  vidrieras,
  vidrierasMessage,
  includeInactive,
}: {
  quinta: Quinta;
  map: QuintaMap | null;
  mapFailed: boolean;
  vidrieras: Vidriera[] | null;
  vidrierasMessage: string | null;
  includeInactive: boolean;
}) {
  const hasBoundary = map?.geometry != null;
  const mappedVidrieras = map
    ? polygonsForOverview(map).filter((polygon) => polygon.kind === "vidriera")
    : [];

  return (
    <div className="space-y-6">
      <Link
        href="/produccion"
        className="text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
      >
        Volver a producción
      </Link>
      <header className="space-y-2">
        <p className="text-sm text-muted">{quinta.code}</p>
        <div className="flex items-center gap-3">
          <h2 className="text-2xl font-semibold">{quinta.name}</h2>
          <StatusBadge active={quinta.active} />
        </div>
        {quinta.notes ? (
          <p className="text-sm leading-6">{quinta.notes}</p>
        ) : (
          <p className="text-sm text-muted">Sin notas.</p>
        )}
      </header>
      <div className="flex flex-wrap gap-3">
        <Link
          href={`/produccion/quintas/${quinta.id}/editar`}
          className="rounded-md border border-line bg-surface px-4 py-2 text-sm font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Editar datos
        </Link>
        <Link
          href={`/produccion/quintas/${quinta.id}/mapa`}
          className="rounded-md border border-line bg-surface px-4 py-2 text-sm font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Editar mapa
        </Link>
        {quinta.active ? (
          <Link
            href={`/produccion/quintas/${quinta.id}/vidrieras/nueva`}
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
      <ActiveToggleForm id={quinta.id} active={quinta.active} kind="quinta" />
      <section className="space-y-3" aria-labelledby="quinta-map-heading">
        <h3 id="quinta-map-heading" className="text-lg font-semibold">
          Mapa
        </h3>
        {mapFailed ? (
          <p role="alert" className="text-sm leading-6 text-warning">
            No se pudo cargar el mapa. Las vidrieras y el resto de la producción
            siguen disponibles.
          </p>
        ) : null}
        {!mapFailed && !hasBoundary ? (
          <div className="space-y-4">
            <EmptyState
              title="Esta quinta todavía no está ubicada"
              body="Marque el límite para ver la quinta y sus vidrieras. La foto aérea y el dibujo están en el editor del mapa."
            />
            <Link
              href={`/produccion/quintas/${quinta.id}/mapa`}
              className="inline-block rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-strong"
            >
              Ubicar en el mapa
            </Link>
          </div>
        ) : null}
        {!mapFailed && hasBoundary && map ? (
          <div className="space-y-3">
            <FarmOverviewLoader mapData={map} />
            <p className="text-sm leading-6 text-muted">
              El polígono es una huella aproximada. No es la superficie medida
              de la quinta ni de las vidrieras.
            </p>
            {mappedVidrieras.length === 0 ? (
              <EmptyState
                title="Ninguna vidriera está dibujada en el mapa"
                body="Las vidrieras sin polígono siguen en el listado. Dibújelas desde Editar mapa."
              />
            ) : null}
          </div>
        ) : null}
      </section>
      <section className="space-y-3">
        <h3 className="text-lg font-semibold">Vidrieras</h3>
        {vidrieras ? (
          <VidrieraList
            quintaId={quinta.id}
            vidrieras={vidrieras}
            allowCreate={quinta.active}
          />
        ) : (
          <p role="alert">{vidrierasMessage}</p>
        )}
      </section>
      <Link
        href={
          includeInactive
            ? `/produccion/quintas/${quinta.id}`
            : `/produccion/quintas/${quinta.id}?incluir_inactivas=1`
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
