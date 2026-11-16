import Link from "next/link";

import {
  activeLabel,
  type Cantero,
  type Quinta,
  type Vidriera,
} from "@/lib/production";

export function FormError({ message }: { message?: string }) {
  if (!message) {
    return null;
  }
  return (
    <p role="alert" className="text-sm leading-6 text-warning">
      {message}
    </p>
  );
}

export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-lg border border-dashed border-line bg-surface px-5 py-6">
      <h2 className="text-base font-semibold">{title}</h2>
      <p className="mt-2 text-sm leading-6 text-muted">{body}</p>
    </div>
  );
}

export function StatusBadge({ active }: { active: boolean }) {
  return (
    <span className="rounded-full border border-line px-2 py-0.5 text-xs text-muted">
      {activeLabel(active)}
    </span>
  );
}

export function QuintaList({ quintas }: { quintas: Quinta[] }) {
  if (quintas.length === 0) {
    return (
      <EmptyState
        title="Todavía no hay quintas"
        body="Cree la primera quinta para empezar el registro. No hay propiedades precargadas."
      />
    );
  }
  return (
    <ul className="divide-y divide-line rounded-lg border border-line bg-surface">
      {quintas.map((quinta) => (
        <li key={quinta.id}>
          <Link
            href={`/produccion/quintas/${quinta.id}`}
            className="flex items-center justify-between gap-4 px-5 py-3 hover:bg-background focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            <span>
              <span className="font-medium">{quinta.name}</span>
              <span className="ml-3 text-sm text-muted">{quinta.code}</span>
            </span>
            <StatusBadge active={quinta.active} />
          </Link>
        </li>
      ))}
    </ul>
  );
}

export function VidrieraList({
  quintaId,
  vidrieras,
  allowCreate,
}: {
  quintaId: string;
  vidrieras: Vidriera[];
  allowCreate: boolean;
}) {
  if (vidrieras.length === 0) {
    return (
      <div className="space-y-4">
        <EmptyState
          title="Esta quinta todavía no tiene vidrieras"
          body="Cree la primera vidriera. El registro genera cuatro canteros, del 1 al 4."
        />
        {allowCreate ? (
          <Link
            href={`/produccion/quintas/${quintaId}/vidrieras/nueva`}
            className="inline-block text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
          >
            Crear la primera vidriera
          </Link>
        ) : null}
      </div>
    );
  }
  return (
    <ul className="divide-y divide-line rounded-lg border border-line bg-surface">
      {vidrieras.map((vidriera) => (
        <li key={vidriera.id}>
          <Link
            href={`/produccion/vidrieras/${vidriera.id}`}
            className="flex items-center justify-between gap-4 px-5 py-3 hover:bg-background focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            <span>
              <span className="font-medium">{vidriera.name}</span>
              <span className="ml-3 text-sm text-muted">{vidriera.code}</span>
            </span>
            <StatusBadge active={vidriera.active} />
          </Link>
        </li>
      ))}
    </ul>
  );
}

export function CanteroList({
  vidrieraId,
  canteros,
}: {
  vidrieraId: string;
  canteros: Cantero[];
}) {
  const ordered = [...canteros].sort(
    (left, right) => left.number - right.number,
  );
  return (
    <ol className="grid gap-3 sm:grid-cols-2">
      {ordered.map((cantero) => (
        <li
          key={cantero.id}
          className="rounded-lg border border-line bg-surface px-4 py-3"
        >
          <p className="text-sm font-semibold">C{cantero.number}</p>
          <p className="mt-1 text-sm text-muted">{cantero.display_code}</p>
          <p className="mt-2 text-sm">
            {cantero.name ?? "Sin nombre descriptivo"}
          </p>
          <div className="mt-3">
            <StatusBadge active={cantero.active} />
          </div>
          <Link
            href={`/produccion/canteros/${cantero.id}/editar?vidriera=${vidrieraId}`}
            className="mt-3 inline-block text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
          >
            Editar cantero
          </Link>
        </li>
      ))}
    </ol>
  );
}

export function TextField({
  id,
  label,
  name,
  defaultValue,
  value,
  onValueChange,
  required = false,
  hint,
}: {
  id: string;
  label: string;
  name: string;
  defaultValue?: string;
  value?: string;
  onValueChange?: (value: string) => void;
  required?: boolean;
  hint?: string;
}) {
  return (
    <div className="space-y-1">
      <label htmlFor={id} className="block text-sm font-medium">
        {label}
      </label>
      <input
        id={id}
        name={name}
        defaultValue={onValueChange ? undefined : defaultValue}
        value={onValueChange ? value : undefined}
        onChange={
          onValueChange
            ? (event) => onValueChange(event.target.value)
            : undefined
        }
        required={required}
        className="w-full rounded-md border border-line bg-surface px-3 py-2 text-sm focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      />
      {hint ? <p className="text-xs leading-5 text-muted">{hint}</p> : null}
    </div>
  );
}

export function NotesField({
  defaultValue,
  value,
  onValueChange,
}: {
  defaultValue?: string;
  value?: string;
  onValueChange?: (value: string) => void;
}) {
  return (
    <div className="space-y-1">
      <label htmlFor="notes" className="block text-sm font-medium">
        Notas o referencia de ubicación
      </label>
      <textarea
        id="notes"
        name="notes"
        defaultValue={onValueChange ? undefined : defaultValue}
        value={onValueChange ? value : undefined}
        onChange={
          onValueChange
            ? (event) => onValueChange(event.target.value)
            : undefined
        }
        rows={3}
        className="w-full rounded-md border border-line bg-surface px-3 py-2 text-sm focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      />
    </div>
  );
}
