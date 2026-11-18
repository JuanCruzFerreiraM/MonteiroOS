import type { BoundaryWarning, QuintaMap } from "@/lib/production";

export type MapDraft =
  | {
      kind: "quinta";
      mode: "replace" | "attach";
      phase: "drawing" | "ready";
    }
  | {
      kind: "vidriera";
      mode: "replace" | "attach";
      vidrieraId: string | null;
      code: string;
      name: string;
      phase: "details" | "drawing" | "ready";
    };

export function MapEditorPanel({
  mapData,
  justCreated,
  draft,
  saving,
  error,
  notices,
  confirmingRemoval,
  onDrawQuinta,
  onEditQuinta,
  onRedrawQuinta,
  onAskRemove,
  onConfirmRemove,
  onCancelRemove,
  onDrawVidriera,
  onEditVidriera,
  onRemoveVidriera,
  onNewVidriera,
  onDraftCode,
  onDraftName,
  onBeginDraw,
  onSave,
  onCancel,
}: {
  mapData: QuintaMap;
  justCreated: boolean;
  draft: MapDraft | null;
  saving: boolean;
  error: string | null;
  notices: BoundaryWarning[];
  confirmingRemoval: string | null;
  onDrawQuinta: () => void;
  onEditQuinta: () => void;
  onRedrawQuinta: () => void;
  onAskRemove: (target: string) => void;
  onConfirmRemove: () => void;
  onCancelRemove: () => void;
  onDrawVidriera: (vidrieraId: string) => void;
  onEditVidriera: (vidrieraId: string) => void;
  onRemoveVidriera: (vidrieraId: string) => void;
  onNewVidriera: () => void;
  onDraftCode: (value: string) => void;
  onDraftName: (value: string) => void;
  onBeginDraw: () => void;
  onSave: () => void;
  onCancel: () => void;
}) {
  const quintaMapped = mapData.geometry !== null;
  const drawing = draft !== null;

  return (
    <section className="space-y-4 rounded-lg border border-line bg-surface p-4">
      {justCreated ? (
        <p className="text-sm leading-6">
          La quinta ya está guardada. Dibuje el límite o continúe sin él desde
          el detalle.
        </p>
      ) : null}
      <div className="space-y-2">
        <h3 className="text-sm font-semibold">Límite de la quinta</h3>
        {quintaMapped ? (
          <p className="text-sm text-muted">Hay un límite guardado.</p>
        ) : (
          <p className="text-sm text-muted">Sin límite geográfico.</p>
        )}
        <div className="flex flex-wrap gap-2">
          {quintaMapped ? (
            <>
              <button
                type="button"
                disabled={drawing || saving}
                onClick={onEditQuinta}
                className="rounded-md border border-line px-3 py-1.5 text-sm disabled:opacity-60"
              >
                Editar límite
              </button>
              <button
                type="button"
                disabled={drawing || saving}
                onClick={onRedrawQuinta}
                className="rounded-md border border-line px-3 py-1.5 text-sm disabled:opacity-60"
              >
                Dibujar de nuevo
              </button>
              <button
                type="button"
                disabled={drawing || saving}
                onClick={() => onAskRemove("quinta")}
                className="rounded-md border border-line px-3 py-1.5 text-sm disabled:opacity-60"
              >
                Quitar límite
              </button>
            </>
          ) : (
            <button
              type="button"
              disabled={drawing || saving}
              onClick={onDrawQuinta}
              className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-white disabled:opacity-60"
            >
              Dibujar límite de la quinta
            </button>
          )}
        </div>
      </div>
      {confirmingRemoval ? (
        <div className="space-y-2 rounded-md border border-line p-3">
          <p className="text-sm leading-6">
            {confirmingRemoval === "quinta"
              ? "¿Quitar el límite de la quinta? La quinta sigue existiendo."
              : "¿Quitar el polígono de esta vidriera? La vidriera sigue existiendo."}
          </p>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={onConfirmRemove}
              className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-white"
            >
              Confirmar
            </button>
            <button
              type="button"
              onClick={onCancelRemove}
              className="rounded-md border border-line px-3 py-1.5 text-sm"
            >
              Cancelar
            </button>
          </div>
        </div>
      ) : null}
      <div className="space-y-2">
        <h3 className="text-sm font-semibold">Vidrieras</h3>
        {!quintaMapped ? (
          <p className="text-sm leading-6">
            Dibuje primero el límite de la quinta. Las vidrieras sin polígono
            siguen en esta lista.
          </p>
        ) : null}
        {mapData.vidrieras.length === 0 ? (
          <p className="text-sm text-muted">Esta quinta no tiene vidrieras.</p>
        ) : (
          <ul className="space-y-3">
            {mapData.vidrieras.map((vidriera) => (
              <li key={vidriera.id} className="space-y-1">
                <p className="text-sm">
                  <span className="font-medium">{vidriera.code}</span>
                  <span className="text-muted"> · {vidriera.name}</span>
                  <span className="text-muted">
                    {vidriera.geometry ? " · Mapeada" : " · Sin límite"}
                  </span>
                </p>
                {vidriera.warnings.map((warning) => (
                  <p
                    key={`${warning.code}-${warning.vidriera_id ?? ""}`}
                    className="border-l-2 border-accent pl-2 text-sm leading-6"
                  >
                    Aviso: {warning.message}
                  </p>
                ))}
                <div className="flex flex-wrap gap-2">
                  {vidriera.geometry ? (
                    <button
                      type="button"
                      disabled={!quintaMapped || drawing || saving}
                      onClick={() => onEditVidriera(vidriera.id)}
                      className="rounded-md border border-line px-3 py-1.5 text-sm disabled:opacity-60"
                    >
                      Editar polígono
                    </button>
                  ) : (
                    <button
                      type="button"
                      disabled={!quintaMapped || drawing || saving}
                      onClick={() => onDrawVidriera(vidriera.id)}
                      className="rounded-md border border-line px-3 py-1.5 text-sm disabled:opacity-60"
                    >
                      Dibujar polígono
                    </button>
                  )}
                  {vidriera.geometry ? (
                    <button
                      type="button"
                      disabled={drawing || saving}
                      onClick={() => onRemoveVidriera(vidriera.id)}
                      className="rounded-md border border-line px-3 py-1.5 text-sm disabled:opacity-60"
                    >
                      Quitar polígono
                    </button>
                  ) : null}
                </div>
              </li>
            ))}
          </ul>
        )}
        <button
          type="button"
          disabled={!mapData.active || !quintaMapped || drawing || saving}
          onClick={onNewVidriera}
          className="rounded-md border border-line px-3 py-1.5 text-sm disabled:opacity-60"
        >
          Nueva vidriera en el mapa
        </button>
        {!mapData.active ? (
          <p className="text-sm text-muted">
            Active la quinta para crear vidrieras.
          </p>
        ) : null}
      </div>
      {draft?.kind === "vidriera" && draft.vidrieraId === null ? (
        <div className="space-y-2">
          <label className="block text-sm font-medium" htmlFor="draft-code">
            Código
            <input
              id="draft-code"
              value={draft.code}
              onChange={(event) => onDraftCode(event.target.value)}
              className="mt-1 block w-full rounded-md border border-line px-3 py-2 text-sm"
            />
          </label>
          <label className="block text-sm font-medium" htmlFor="draft-name">
            Nombre
            <input
              id="draft-name"
              value={draft.name}
              onChange={(event) => onDraftName(event.target.value)}
              className="mt-1 block w-full rounded-md border border-line px-3 py-2 text-sm"
            />
          </label>
          {draft.phase === "details" ? (
            <button
              type="button"
              onClick={onBeginDraw}
              className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-white"
            >
              Dibujar polígono
            </button>
          ) : null}
        </div>
      ) : null}
      {draft ? (
        <div className="space-y-2">
          <p className="text-sm leading-6">
            Marque los vértices y cierre el contorno en el primer punto.
            Cancelar no crea una vidriera ni reemplaza un límite guardado.
          </p>
          <div className="flex gap-2">
            <button
              type="button"
              disabled={saving || draft.phase !== "ready"}
              onClick={onSave}
              className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-white disabled:opacity-60"
            >
              {saving ? "Guardando…" : "Guardar polígono"}
            </button>
            <button
              type="button"
              disabled={saving}
              onClick={onCancel}
              className="rounded-md border border-line px-3 py-1.5 text-sm"
            >
              Cancelar
            </button>
          </div>
        </div>
      ) : null}
      {error ? (
        <p role="alert" className="text-sm leading-6 text-warning">
          {error}
        </p>
      ) : null}
      {notices.map((notice) => (
        <p
          key={`${notice.code}-${notice.vidriera_id ?? "quinta"}`}
          role="status"
          className="border-l-2 border-accent pl-2 text-sm leading-6"
        >
          Aviso: {notice.message}
        </p>
      ))}
    </section>
  );
}
