"use client";

import { useActionState, useState } from "react";

import {
  createQuinta,
  createVidriera,
  setQuintaActive,
  setVidrieraActive,
  updateCantero,
  updateQuinta,
  updateVidriera,
} from "@/app/produccion/actions";
import {
  FormError,
  NotesField,
  TextField,
} from "@/components/production/production-views";
import { SubmitButton } from "@/components/submit-button";
import type { FormState } from "@/lib/production";

const initialState: FormState = {};

export function QuintaCreateForm() {
  const [state, action] = useActionState(createQuinta, initialState);
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [notes, setNotes] = useState("");
  return (
    <form action={action} className="max-w-xl space-y-4">
      <FormError message={state.error} />
      <TextField
        id="code"
        name="code"
        label="Código operativo"
        required
        value={code}
        onValueChange={setCode}
        hint="De 2 a 12 letras o dígitos, empezando con una letra. Ejemplo: VE. No se puede cambiar después."
      />
      <TextField
        id="name"
        name="name"
        label="Nombre"
        required
        value={name}
        onValueChange={setName}
      />
      <NotesField value={notes} onValueChange={setNotes} />
      <SubmitButton label="Crear quinta" />
    </form>
  );
}

export function QuintaEditForm({
  id,
  name,
  notes,
}: {
  id: string;
  name: string;
  notes: string | null;
}) {
  const [state, action] = useActionState(updateQuinta, initialState);
  const [nameValue, setNameValue] = useState(name);
  const [notesValue, setNotesValue] = useState(notes ?? "");
  return (
    <form action={action} className="max-w-xl space-y-4">
      <FormError message={state.error} />
      <input type="hidden" name="id" value={id} />
      <TextField
        id="name"
        name="name"
        label="Nombre"
        required
        value={nameValue}
        onValueChange={setNameValue}
      />
      <NotesField value={notesValue} onValueChange={setNotesValue} />
      <SubmitButton label="Guardar cambios" />
    </form>
  );
}

export function ActiveToggleForm({
  id,
  active,
  kind,
}: {
  id: string;
  active: boolean;
  kind: "quinta" | "vidriera";
}) {
  const action = kind === "quinta" ? setQuintaActive : setVidrieraActive;
  const [state, formAction] = useActionState(action, initialState);
  return (
    <form action={formAction} className="space-y-2">
      <FormError message={state.error} />
      <input type="hidden" name="id" value={id} />
      <input type="hidden" name="active" value={active ? "false" : "true"} />
      <SubmitButton label={active ? "Desactivar" : "Volver a activar"} />
    </form>
  );
}

export function VidrieraCreateForm({
  quintaId,
  suggestedCode,
}: {
  quintaId: string;
  suggestedCode: string;
}) {
  const [state, action] = useActionState(createVidriera, initialState);
  const [code, setCode] = useState(suggestedCode);
  const [name, setName] = useState("");
  const [notes, setNotes] = useState("");
  return (
    <form action={action} className="max-w-xl space-y-4">
      <FormError message={state.error} />
      <input type="hidden" name="quinta_id" value={quintaId} />
      <p className="text-sm leading-6 text-muted">
        Al guardar se crean cuatro canteros, numerados del 1 al 4. El código
        sugerido se puede reemplazar por otro código libre de esta quinta antes
        de crear la vidriera.
      </p>
      <TextField
        id="code"
        name="code"
        label="Código operativo"
        required
        value={code}
        onValueChange={setCode}
        hint="Formato QUINTA-V001. No se puede cambiar después."
      />
      <TextField
        id="name"
        name="name"
        label="Nombre"
        required
        value={name}
        onValueChange={setName}
      />
      <NotesField value={notes} onValueChange={setNotes} />
      <SubmitButton label="Crear vidriera" />
    </form>
  );
}

export function VidrieraEditForm({
  id,
  name,
  notes,
}: {
  id: string;
  name: string;
  notes: string | null;
}) {
  const [state, action] = useActionState(updateVidriera, initialState);
  const [nameValue, setNameValue] = useState(name);
  const [notesValue, setNotesValue] = useState(notes ?? "");
  return (
    <form action={action} className="max-w-xl space-y-4">
      <FormError message={state.error} />
      <input type="hidden" name="id" value={id} />
      <TextField
        id="name"
        name="name"
        label="Nombre"
        required
        value={nameValue}
        onValueChange={setNameValue}
      />
      <NotesField value={notesValue} onValueChange={setNotesValue} />
      <SubmitButton label="Guardar cambios" />
    </form>
  );
}

export function CanteroEditForm({
  id,
  vidrieraId,
  name,
  active,
}: {
  id: string;
  vidrieraId: string;
  name: string | null;
  active: boolean;
}) {
  const [state, action] = useActionState(updateCantero, initialState);
  const [nameValue, setNameValue] = useState(name ?? "");
  const [activeValue, setActiveValue] = useState(active);
  return (
    <form action={action} className="max-w-xl space-y-4">
      <FormError message={state.error} />
      <input type="hidden" name="id" value={id} />
      <input type="hidden" name="vidriera_id" value={vidrieraId} />
      <TextField
        id="name"
        name="name"
        label="Nombre descriptivo"
        value={nameValue}
        onValueChange={setNameValue}
        hint="Opcional. El número del cantero no cambia."
      />
      <label className="flex items-center gap-2 text-sm" htmlFor="active">
        <input
          id="active"
          name="active"
          type="checkbox"
          checked={activeValue}
          onChange={(event) => setActiveValue(event.target.checked)}
          className="size-4 accent-accent"
        />
        Activo
      </label>
      <SubmitButton label="Guardar cantero" />
    </form>
  );
}
