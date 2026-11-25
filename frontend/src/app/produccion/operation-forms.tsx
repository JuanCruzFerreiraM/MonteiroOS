"use client";

import { useActionState, useState } from "react";

import {
  createOperation,
  updateOperation,
} from "@/app/produccion/operation-actions";
import { FormError } from "@/components/production/production-views";
import { SubmitButton } from "@/components/submit-button";
import {
  OPERATION_TYPES,
  acceptsInterval,
  operationLabel,
  toLocalInput,
  type Operation,
} from "@/lib/operations";
import type { FormState } from "@/lib/production";

const initialState: FormState = {};

const fieldClass =
  "w-full rounded-md border border-line bg-surface px-3 py-2 text-sm focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent";

export type CycleChoice = {
  id: string;
  label: string;
};

export function OperationCreateForm({
  vidrieraId,
  cycles,
  defaultCycleId,
  initialType = "irrigation",
}: {
  vidrieraId: string;
  cycles: CycleChoice[];
  defaultCycleId: string | null;
  initialType?: string;
}) {
  const [state, action] = useActionState(createOperation, initialState);
  const [type, setType] = useState<string>(initialType);
  return (
    <form action={action} className="max-w-xl space-y-4">
      <FormError message={state.error} />
      <input type="hidden" name="vidriera_id" value={vidrieraId} />
      <TypeField value={type} onChange={setType} />
      <MomentField
        id="occurred-at"
        name="occurred_at"
        label="Fecha y hora"
        required
      />
      <CycleField cycles={cycles} defaultValue={defaultCycleId ?? ""} />
      <p className="text-xs leading-5 text-muted">
        Si hay un ciclo activo, queda elegido. Puede dejar la operación sin
        ciclo.
      </p>
      {acceptsInterval(type) ? <IntervalFields /> : null}
      <NotesField id="operation-notes" />
      <SubmitButton label="Registrar operación" />
    </form>
  );
}

export function OperationEditForm({
  operation,
  cycles,
}: {
  operation: Operation;
  cycles: CycleChoice[];
}) {
  const [state, action] = useActionState(updateOperation, initialState);
  const [type, setType] = useState<string>(operation.operation_type);
  const scheduled = operation.origin === "scheduled";
  return (
    <form action={action} className="max-w-xl space-y-4">
      <FormError message={state.error} />
      <input type="hidden" name="operation_id" value={operation.id} />
      {scheduled ? (
        <input type="hidden" name="origin" value="scheduled" />
      ) : null}
      {scheduled ? (
        <div className="space-y-1">
          <p className="text-sm font-medium">Tipo</p>
          <p className="text-sm">{operation.operation_label}</p>
        </div>
      ) : (
        <TypeField value={type} onChange={setType} />
      )}
      {scheduled ? null : (
        <MomentField
          id="occurred-at"
          name="occurred_at"
          label="Fecha y hora"
          defaultValue={toLocalInput(operation.occurred_at)}
          required
        />
      )}
      <CycleField cycles={cycles} defaultValue={operation.cycle_id ?? ""} />
      {scheduled ? (
        <IntervalFields
          start={toLocalInput(operation.interval_start)}
          end={toLocalInput(operation.interval_end)}
          required
          note="El inicio real es la fecha de la operación. Corregirlo no cambia el horario programado."
        />
      ) : null}
      {!scheduled && acceptsInterval(type) ? (
        <IntervalFields
          start={toLocalInput(operation.interval_start)}
          end={toLocalInput(operation.interval_end)}
        />
      ) : null}
      <NotesField id="operation-notes" defaultValue={operation.notes ?? ""} />
      <SubmitButton label="Guardar corrección" />
    </form>
  );
}

function TypeField({
  value,
  onChange,
}: {
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="space-y-1">
      <label htmlFor="operation-type" className="block text-sm font-medium">
        Tipo
      </label>
      <select
        id="operation-type"
        name="operation_type"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className={fieldClass}
      >
        {OPERATION_TYPES.map((type) => (
          <option key={type} value={type}>
            {operationLabel(type)}
          </option>
        ))}
      </select>
    </div>
  );
}

function MomentField({
  id,
  name,
  label,
  defaultValue,
  required = false,
}: {
  id: string;
  name: string;
  label: string;
  defaultValue?: string;
  required?: boolean;
}) {
  return (
    <div className="space-y-1">
      <label htmlFor={id} className="block text-sm font-medium">
        {label}
      </label>
      <input
        id={id}
        name={name}
        type="datetime-local"
        required={required}
        defaultValue={defaultValue}
        className={fieldClass}
      />
    </div>
  );
}

function CycleField({
  cycles,
  defaultValue,
}: {
  cycles: CycleChoice[];
  defaultValue: string;
}) {
  return (
    <div className="space-y-1">
      <label htmlFor="cycle-id" className="block text-sm font-medium">
        Ciclo
      </label>
      <select
        id="cycle-id"
        name="cycle_id"
        defaultValue={defaultValue}
        className={fieldClass}
      >
        <option value="">Sin ciclo</option>
        {cycles.map((cycle) => (
          <option key={cycle.id} value={cycle.id}>
            {cycle.label}
          </option>
        ))}
      </select>
    </div>
  );
}

function IntervalFields({
  start = "",
  end = "",
  required = false,
  note = "El intervalo real es opcional. Si lo completa, indique inicio y fin. Un turno que cruza la medianoche termina al día siguiente.",
}: {
  start?: string;
  end?: string;
  required?: boolean;
  note?: string;
}) {
  return (
    <div className="space-y-3">
      <p className="text-sm leading-6 text-muted">{note}</p>
      <MomentField
        id="interval-start"
        name="interval_start"
        label="Inicio real"
        defaultValue={start}
        required={required}
      />
      <MomentField
        id="interval-end"
        name="interval_end"
        label="Fin real"
        defaultValue={end}
        required={required}
      />
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
        rows={3}
        defaultValue={defaultValue}
        className={fieldClass}
      />
    </div>
  );
}
