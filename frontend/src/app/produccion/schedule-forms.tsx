"use client";

import { useActionState } from "react";

import {
  createSchedule,
  endSchedule,
  pauseSchedule,
  resumeSchedule,
  reviseSchedule,
} from "@/app/produccion/schedule-actions";
import { FormError } from "@/components/production/production-views";
import { SubmitButton } from "@/components/submit-button";
import { operationLabel } from "@/lib/operations";
import { WEEKDAYS, clockInput, type ScheduleRevision } from "@/lib/schedules";
import type { FormState } from "@/lib/production";

const initialState: FormState = {};

const fieldClass =
  "w-full rounded-md border border-line bg-surface px-3 py-2 text-sm focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent";

export function ScheduleCreateForm({
  vidrieraId,
  defaultStart,
  defaultEnd,
}: {
  vidrieraId: string;
  defaultStart: string;
  defaultEnd: string;
}) {
  const [state, action] = useActionState(createSchedule, initialState);
  return (
    <form action={action} className="max-w-xl space-y-4">
      <FormError message={state.error} />
      <input type="hidden" name="vidriera_id" value={vidrieraId} />
      <TypeField />
      <PeriodFields start={defaultStart} end={defaultEnd} />
      <WeekdayFields selected={[1, 2, 3, 4, 5, 6, 7]} />
      <ClockFields start="22:00" end="02:00" />
      <p className="text-xs leading-5 text-muted">
        Si el fin es anterior al inicio, el turno termina al día siguiente. El
        día de la ocurrencia es el del inicio.
      </p>
      <NotesField />
      <SubmitButton label="Guardar programación" />
    </form>
  );
}

export function ScheduleReviseForm({
  revision,
  defaultFrom,
}: {
  revision: ScheduleRevision;
  defaultFrom: string;
}) {
  const [state, action] = useActionState(reviseSchedule, initialState);
  return (
    <form action={action} className="max-w-xl space-y-4">
      <FormError message={state.error} />
      <input type="hidden" name="series_id" value={revision.series_id} />
      <div className="space-y-1">
        <label htmlFor="effective-from" className="block text-sm font-medium">
          Rige desde
        </label>
        <input
          id="effective-from"
          name="effective_from"
          type="date"
          required
          defaultValue={defaultFrom}
          className={fieldClass}
        />
      </div>
      <p className="text-xs leading-5 text-muted">
        Los días anteriores conservan el horario que ya estaba vigente.
      </p>
      <PeriodEnd end={revision.effective_end} />
      <WeekdayFields selected={revision.weekdays} />
      <ClockFields
        start={clockInput(revision.start_time)}
        end={clockInput(revision.end_time)}
      />
      <NotesField defaultValue={revision.notes ?? ""} />
      <SubmitButton label="Guardar cambio" />
    </form>
  );
}

export function ScheduleLifecycleForms({
  revision,
  defaultFrom,
}: {
  revision: ScheduleRevision;
  defaultFrom: string;
}) {
  return (
    <div className="space-y-4">
      {revision.status === "active" ? (
        <LifecycleForm
          action={pauseSchedule}
          seriesId={revision.series_id}
          field="effective_from"
          label="Pausar desde"
          defaultValue={defaultFrom}
          submit="Pausar"
        />
      ) : null}
      {revision.status === "paused" ? (
        <LifecycleForm
          action={resumeSchedule}
          seriesId={revision.series_id}
          field="effective_from"
          label="Reanudar desde"
          defaultValue={defaultFrom}
          submit="Reanudar"
        />
      ) : null}
      {revision.status !== "ended" ? (
        <LifecycleForm
          action={endSchedule}
          seriesId={revision.series_id}
          field="effective_end"
          label="Finalizar el"
          defaultValue={revision.effective_end}
          submit="Finalizar"
        />
      ) : (
        <p className="text-sm text-muted">Esta programación ya finalizó.</p>
      )}
    </div>
  );
}

function LifecycleForm({
  action,
  seriesId,
  field,
  label,
  defaultValue,
  submit,
}: {
  action: typeof pauseSchedule;
  seriesId: string;
  field: "effective_from" | "effective_end";
  label: string;
  defaultValue: string;
  submit: string;
}) {
  const [state, formAction] = useActionState(action, initialState);
  return (
    <form action={formAction} className="flex flex-wrap items-end gap-3">
      <FormError message={state.error} />
      <input type="hidden" name="series_id" value={seriesId} />
      <div className="space-y-1">
        <label htmlFor={field} className="block text-sm font-medium">
          {label}
        </label>
        <input
          id={field}
          name={field}
          type="date"
          required
          defaultValue={defaultValue}
          className={fieldClass}
        />
      </div>
      <SubmitButton label={submit} />
    </form>
  );
}

function TypeField() {
  return (
    <div className="space-y-1">
      <label htmlFor="schedule-type" className="block text-sm font-medium">
        Operación
      </label>
      <select id="schedule-type" name="operation_type" className={fieldClass}>
        <option value="artificial_lighting">
          {operationLabel("artificial_lighting")}
        </option>
        <option value="black_nylon">{operationLabel("black_nylon")}</option>
      </select>
    </div>
  );
}

function PeriodFields({ start, end }: { start: string; end: string }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      <DateField
        id="effective-start"
        name="effective_start"
        label="Desde"
        defaultValue={start}
      />
      <DateField
        id="effective-end"
        name="effective_end"
        label="Hasta"
        defaultValue={end}
      />
    </div>
  );
}

function PeriodEnd({ end }: { end: string }) {
  return (
    <DateField
      id="effective-end"
      name="effective_end"
      label="Hasta"
      defaultValue={end}
    />
  );
}

function DateField({
  id,
  name,
  label,
  defaultValue,
}: {
  id: string;
  name: string;
  label: string;
  defaultValue: string;
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
        required
        defaultValue={defaultValue}
        className={fieldClass}
      />
    </div>
  );
}

function WeekdayFields({ selected }: { selected: number[] }) {
  return (
    <fieldset className="space-y-2">
      <legend className="text-sm font-medium">Días</legend>
      <div className="flex flex-wrap gap-3">
        {WEEKDAYS.map((day) => (
          <label key={day.value} className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              name="weekdays"
              value={day.value}
              defaultChecked={selected.includes(day.value)}
            />
            {day.label}
          </label>
        ))}
      </div>
    </fieldset>
  );
}

function ClockFields({ start, end }: { start: string; end: string }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      <div className="space-y-1">
        <label htmlFor="start-time" className="block text-sm font-medium">
          Hora de inicio
        </label>
        <input
          id="start-time"
          name="start_time"
          type="time"
          required
          defaultValue={start}
          className={fieldClass}
        />
      </div>
      <div className="space-y-1">
        <label htmlFor="end-time" className="block text-sm font-medium">
          Hora de fin
        </label>
        <input
          id="end-time"
          name="end_time"
          type="time"
          required
          defaultValue={end}
          className={fieldClass}
        />
      </div>
    </div>
  );
}

function NotesField({ defaultValue = "" }: { defaultValue?: string }) {
  return (
    <div className="space-y-1">
      <label htmlFor="schedule-notes" className="block text-sm font-medium">
        Notas
      </label>
      <textarea
        id="schedule-notes"
        name="notes"
        rows={3}
        defaultValue={defaultValue}
        className={fieldClass}
      />
    </div>
  );
}
