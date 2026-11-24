"use client";

import { useActionState } from "react";

import {
  correctCycle,
  finalizeCycle,
  startCycle,
} from "@/app/produccion/cycle-actions";
import { FormError } from "@/components/production/production-views";
import { SubmitButton } from "@/components/submit-button";
import type { CultivationCycle } from "@/lib/cycles";
import type { FormState } from "@/lib/production";

const initialState: FormState = {};

const fieldClass =
  "w-full rounded-md border border-line bg-surface px-3 py-2 text-sm focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent";

export function StartCycleForm({ vidrieraId }: { vidrieraId: string }) {
  const [state, action] = useActionState(startCycle, initialState);
  return (
    <form action={action} className="max-w-xl space-y-4">
      <FormError message={state.error} />
      <input type="hidden" name="vidriera_id" value={vidrieraId} />
      <DateField
        id="planting-date"
        name="start_date"
        label="Fecha de plantación"
        required
        hint="Es el día en que se plantó la vidriera."
      />
      <NotesField id="planting-notes" />
      <SubmitButton label="Iniciar ciclo" />
    </form>
  );
}

export function FinalizeCycleForm({
  cycleId,
  vidrieraId,
  startDate,
  suggestedEndDate,
}: {
  cycleId: string;
  vidrieraId: string;
  startDate: string;
  suggestedEndDate: string;
}) {
  const [state, action] = useActionState(finalizeCycle, initialState);
  return (
    <form action={action} className="max-w-xl space-y-4">
      <p className="text-sm leading-6 text-muted">
        El cierre no es automático. Indique la fecha real y confirme.
      </p>
      <FormError message={state.error} />
      <input type="hidden" name="cycle_id" value={cycleId} />
      <input type="hidden" name="vidriera_id" value={vidrieraId} />
      <input type="hidden" name="start_date" value={startDate} />
      <DateField
        id={`closing-date-${cycleId}`}
        name="end_date"
        label="Fecha de cierre"
        required
        defaultValue={suggestedEndDate}
        hint="Puede cambiar la fecha sugerida antes de confirmar."
      />
      <label className="flex items-start gap-2 text-sm leading-6">
        <input type="checkbox" name="confirm" required className="mt-1" />
        Confirmo que este ciclo termina en la fecha indicada.
      </label>
      <SubmitButton label="Finalizar ciclo" />
    </form>
  );
}

export function CorrectCycleForm({ cycle }: { cycle: CultivationCycle }) {
  const [state, action] = useActionState(correctCycle, initialState);
  const active = cycle.status === "active";
  return (
    <form action={action} className="max-w-xl space-y-4">
      <p className="text-sm leading-6 text-muted">
        {active
          ? "Puede corregir la plantación y las notas. Para cerrarlo, finalícelo."
          : "Puede corregir la plantación, el cierre y las notas. El ciclo sigue finalizado y en la misma vidriera."}
      </p>
      <FormError message={state.error} />
      <input type="hidden" name="cycle_id" value={cycle.id} />
      <input type="hidden" name="vidriera_id" value={cycle.vidriera_id} />
      <input type="hidden" name="status" value={cycle.status} />
      <DateField
        id={`correct-start-${cycle.id}`}
        name="start_date"
        label="Fecha de plantación"
        required
        defaultValue={cycle.start_date}
      />
      {active ? null : (
        <DateField
          id={`correct-end-${cycle.id}`}
          name="end_date"
          label="Fecha de cierre"
          required
          defaultValue={cycle.end_date ?? ""}
        />
      )}
      <NotesField
        id={`correct-notes-${cycle.id}`}
        defaultValue={cycle.notes ?? ""}
      />
      <SubmitButton label="Guardar corrección" />
    </form>
  );
}

function DateField({
  id,
  name,
  label,
  required = false,
  defaultValue,
  hint,
}: {
  id: string;
  name: string;
  label: string;
  required?: boolean;
  defaultValue?: string;
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
        type="date"
        required={required}
        defaultValue={defaultValue}
        className={fieldClass}
      />
      {hint ? <p className="text-xs leading-5 text-muted">{hint}</p> : null}
    </div>
  );
}

function NotesField({
  id,
  defaultValue,
}: {
  id: string;
  defaultValue?: string;
}) {
  return (
    <div className="space-y-1">
      <label htmlFor={id} className="block text-sm font-medium">
        Notas
      </label>
      <textarea
        id={id}
        name="notes"
        defaultValue={defaultValue}
        rows={3}
        className={fieldClass}
      />
    </div>
  );
}
