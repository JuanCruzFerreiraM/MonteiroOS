"use client";

import { useActionState, useState } from "react";

import { resolveOccurrences } from "@/app/produccion/confirmation-actions";
import { FormError } from "@/components/production/production-views";
import { toLocalInput } from "@/lib/operations";
import { occurrenceStatusLabel, type Occurrence } from "@/lib/schedules";

const initialState = {};

const fieldClass =
  "w-full rounded-md border border-line bg-surface px-3 py-2 text-sm focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent";

export type CycleChoice = { id: string; label: string };

export function OccurrenceBoard({
  vidrieraId,
  occurrences,
  cycles,
}: {
  vidrieraId: string;
  occurrences: Occurrence[];
  cycles: CycleChoice[];
}) {
  const [state, action] = useActionState(resolveOccurrences, initialState);
  const [selected, setSelected] = useState<string[]>([]);
  const selectable = occurrences.filter((item) => item.status === "unverified");
  const chosen = selectable.filter((item) => selected.includes(keyOf(item)));

  function toggle(value: string) {
    setSelected((current) =>
      current.includes(value)
        ? current.filter((item) => item !== value)
        : [...current, value],
    );
  }

  if (occurrences.length === 0) {
    return (
      <p className="text-sm text-muted">No hay ocurrencias en este período.</p>
    );
  }

  return (
    <form action={action} className="space-y-4">
      <FormError message={state.error} />
      {state.notice ? <p role="status">{state.notice}</p> : null}
      <input type="hidden" name="vidriera_id" value={vidrieraId} />
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="border-b border-line text-left text-muted">
            <th className="px-2 py-2 font-medium">Elegir</th>
            <th className="px-2 py-2 font-medium">Fecha</th>
            <th className="px-2 py-2 font-medium">Operación</th>
            <th className="px-2 py-2 font-medium">Estado</th>
            <th className="px-2 py-2 font-medium">Previsto</th>
          </tr>
        </thead>
        <tbody>
          {occurrences.map((item) => {
            const value = keyOf(item);
            const future = item.status === "scheduled";
            return (
              <tr
                key={value}
                className={
                  future
                    ? "border-b border-line text-muted"
                    : "border-b border-line"
                }
              >
                <td className="px-2 py-2">
                  {item.status === "unverified" ? (
                    <input
                      type="checkbox"
                      name="occurrence"
                      value={value}
                      checked={selected.includes(value)}
                      onChange={() => toggle(value)}
                      aria-label={`${item.operation_label} ${item.occurrence_date}`}
                    />
                  ) : (
                    <span className="text-muted">—</span>
                  )}
                </td>
                <td className="px-2 py-2">{item.occurrence_date}</td>
                <td className="px-2 py-2">{item.operation_label}</td>
                <td className="px-2 py-2">
                  {occurrenceStatusLabel(item.status)}
                </td>
                <td className="px-2 py-2">
                  {toLocalInput(item.expected_start)} –{" "}
                  {toLocalInput(item.expected_end)}
                  {item.status === "confirmed" &&
                  item.actual_start &&
                  item.actual_end
                    ? ` · Real ${toLocalInput(item.actual_start)} – ${toLocalInput(item.actual_end)}`
                    : ""}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <section className="space-y-3 rounded-lg border border-line bg-surface p-4">
        <h3 className="text-sm font-semibold">Revisar selección</h3>
        {chosen.length === 0 ? (
          <p className="text-sm text-muted">No hay ocurrencias elegidas.</p>
        ) : (
          <ul className="space-y-1 text-sm">
            {chosen.map((item) => (
              <li key={keyOf(item)}>
                {item.occurrence_date} · {item.operation_label}
              </li>
            ))}
          </ul>
        )}
        {chosen.length > 1 ? (
          <p className="text-sm leading-6 text-muted">
            La confirmación grupal usa el horario programado como valor
            supuesto. No es una medición. El ciclo queda vacío y puede
            corregirse después.
          </p>
        ) : null}
        {chosen.length === 1 ? (
          <SingleFields occurrence={chosen[0]} cycles={cycles} />
        ) : null}
        <div className="flex flex-wrap gap-3">
          <button
            type="submit"
            name="outcome"
            value="confirmed"
            className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-strong focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            Confirmar seleccionadas
          </button>
          <button
            type="submit"
            name="outcome"
            value="not_occurred"
            className="rounded-md border border-line bg-surface px-4 py-2 text-sm font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            Marcar como no realizadas
          </button>
        </div>
      </section>
    </form>
  );
}

function SingleFields({
  occurrence,
  cycles,
}: {
  occurrence: Occurrence;
  cycles: CycleChoice[];
}) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      <p className="sm:col-span-2 text-sm leading-6 text-muted">
        El horario inicial copia la programación y queda marcado como supuesto
        si no lo cambia.
      </p>
      <div className="space-y-1">
        <label htmlFor="actual-start" className="block text-sm font-medium">
          Inicio real
        </label>
        <input
          id="actual-start"
          name="actual_start"
          type="datetime-local"
          defaultValue={toLocalInput(occurrence.expected_start)}
          className={fieldClass}
        />
      </div>
      <div className="space-y-1">
        <label htmlFor="actual-end" className="block text-sm font-medium">
          Fin real
        </label>
        <input
          id="actual-end"
          name="actual_end"
          type="datetime-local"
          defaultValue={toLocalInput(occurrence.expected_end)}
          className={fieldClass}
        />
      </div>
      <div className="space-y-1 sm:col-span-2">
        <label htmlFor="confirm-cycle" className="block text-sm font-medium">
          Ciclo
        </label>
        <select
          id="confirm-cycle"
          name="cycle_id"
          defaultValue={occurrence.suggested_cycle_id ?? ""}
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
    </div>
  );
}

function keyOf(item: Occurrence): string {
  return `${item.series_id}|${item.occurrence_date}|${item.expected_start}|${item.expected_end}`;
}
