import Link from "next/link";

import type { ImageryPublicConfig, PlaceSearchResult } from "@/lib/imagery";

export function MapStatus({
  imagery,
  tileError,
  mapFailed,
  geometryError,
  hasBoundary,
  query,
  onQueryChange,
  onSearch,
  searching,
  searchError,
  results,
  onSelectResult,
}: {
  imagery: ImageryPublicConfig;
  tileError: boolean;
  mapFailed: boolean;
  geometryError: boolean;
  hasBoundary: boolean;
  query: string;
  onQueryChange: (value: string) => void;
  onSearch: () => void;
  searching: boolean;
  searchError: string | null;
  results: PlaceSearchResult[];
  onSelectResult: (result: PlaceSearchResult) => void;
}) {
  return (
    <div className="space-y-3">
      <p className="text-sm leading-6 text-muted">
        El polígono es una huella aproximada. No es la superficie medida de la
        quinta ni de las vidrieras.
      </p>
      {imagery.message ? (
        <p role="alert" className="text-sm leading-6 text-warning">
          {imagery.message}
        </p>
      ) : null}
      {tileError ? (
        <p role="alert" className="text-sm leading-6 text-warning">
          No se pudieron cargar algunas imágenes satelitales. Los límites
          guardados no se modificaron.
        </p>
      ) : null}
      {mapFailed ? (
        <p role="alert" className="text-sm leading-6 text-warning">
          No se pudo iniciar el mapa. Los datos guardados no se modificaron.
        </p>
      ) : null}
      {geometryError ? (
        <p role="alert" className="text-sm leading-6 text-warning">
          Hay un límite guardado que no se pudo dibujar. No se modificó.
        </p>
      ) : null}
      {!hasBoundary ? (
        <p className="text-sm leading-6">
          Esta quinta todavía no tiene un límite dibujado. Busque el lugar o
          mueva el mapa. La falta de imagen no significa que no haya un límite
          guardado.
        </p>
      ) : null}
      <form
        className="flex flex-wrap items-end gap-3"
        onSubmit={(event) => {
          event.preventDefault();
          onSearch();
        }}
      >
        <label className="block text-sm font-medium" htmlFor="map-search">
          Buscar lugar
          <input
            id="map-search"
            value={query}
            disabled={!imagery.searchEnabled || searching}
            onChange={(event) => onQueryChange(event.target.value)}
            placeholder="Villa Elisa o Arturo Seguí"
            className="mt-1 block w-72 rounded-md border border-line bg-surface px-3 py-2 text-sm disabled:text-muted"
          />
        </label>
        <button
          type="submit"
          disabled={!imagery.searchEnabled || searching}
          className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-strong disabled:opacity-60"
        >
          {searching ? "Buscando…" : "Buscar"}
        </button>
      </form>
      {!imagery.searchEnabled ? (
        <p className="text-sm text-muted">
          La búsqueda geográfica necesita la clave del proveedor de imágenes.
        </p>
      ) : null}
      {searchError ? (
        <p role="alert" className="text-sm leading-6 text-warning">
          {searchError}
        </p>
      ) : null}
      {results.length > 0 ? (
        <ul className="flex flex-wrap gap-2">
          {results.map((result) => (
            <li key={`${result.latitude},${result.longitude},${result.label}`}>
              <button
                type="button"
                onClick={() => onSelectResult(result)}
                className="rounded-md border border-line bg-surface px-3 py-1 text-sm hover:bg-background"
              >
                {result.label}
              </button>
            </li>
          ))}
        </ul>
      ) : null}
      <Link
        href="/produccion"
        className="inline-block text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
      >
        Volver al listado de producción
      </Link>
    </div>
  );
}
