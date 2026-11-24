"use server";

import { revalidatePath } from "next/cache";
import { unstable_rethrow } from "next/navigation";

import { backendFetch, optionalText, readApiError } from "@/lib/backend";
import { fromLocalInput, intervalError } from "@/lib/operations";

export type ConfirmationState = {
  error?: string;
  notice?: string;
};

type ResolveResult = {
  occurrence_date: string;
  status: "confirmed" | "not_occurred" | "unchanged" | "conflict" | "invalid";
  message: string | null;
};

export async function resolveOccurrences(
  _state: ConfirmationState,
  formData: FormData,
): Promise<ConfirmationState> {
  const vidrieraId = String(formData.get("vidriera_id") ?? "");
  const outcome = String(formData.get("outcome") ?? "");
  const selected = formData.getAll("occurrence").map(String).filter(Boolean);
  if (selected.length === 0) {
    return { error: "Seleccione al menos una ocurrencia." };
  }
  if (outcome !== "confirmed" && outcome !== "not_occurred") {
    return { error: "Elija confirmar o marcar que no se realizó." };
  }
  const items: Record<string, unknown>[] = [];
  for (const value of selected) {
    const [seriesId, occurrenceDate, expectedStart, expectedEnd] =
      value.split("|");
    const item: Record<string, unknown> = {
      series_id: seriesId,
      occurrence_date: occurrenceDate,
      outcome,
    };
    if (outcome === "confirmed" && selected.length === 1) {
      const timing = actualTiming(formData, expectedStart, expectedEnd);
      if (timing.error) {
        return { error: timing.error };
      }
      Object.assign(item, timing.fields);
      item.cycle_id = optionalText(formData.get("cycle_id"));
    } else if (outcome === "confirmed") {
      item.timing_basis = "assumed_from_schedule";
    }
    items.push(item);
  }
  try {
    const response = await backendFetch(
      `/api/operations/vidrieras/${vidrieraId}/occurrences/resolve-batch`,
      { method: "POST", body: JSON.stringify({ items }) },
    );
    if (!response.ok) {
      return { error: await readApiError(response) };
    }
    const results = (await response.json()) as ResolveResult[];
    revalidatePath(`/produccion/vidrieras/${vidrieraId}/confirmaciones`);
    revalidatePath(`/produccion/vidrieras/${vidrieraId}`);
    return { notice: summarize(results) };
  } catch (error) {
    unstable_rethrow(error);
    return { error: "No se pudo completar la operación." };
  }
}

function actualTiming(
  formData: FormData,
  expectedStart: string,
  expectedEnd: string,
): { error?: string; fields: Record<string, string> } {
  const start = String(formData.get("actual_start") ?? "");
  const end = String(formData.get("actual_end") ?? "");
  if (!start && !end) {
    return { fields: { timing_basis: "assumed_from_schedule" } };
  }
  const invalid = intervalError(start, end);
  if (invalid) {
    return { error: invalid, fields: {} };
  }
  const startIso = fromLocalInput(start);
  const endIso = fromLocalInput(end);
  if (!startIso || !endIso) {
    return {
      error: "El intervalo real debe ser una fecha y hora válida.",
      fields: {},
    };
  }
  const same =
    Date.parse(startIso) === Date.parse(expectedStart) &&
    Date.parse(endIso) === Date.parse(expectedEnd);
  if (same) {
    return { fields: { timing_basis: "assumed_from_schedule" } };
  }
  return {
    fields: {
      timing_basis: "operator_entered",
      actual_start: startIso,
      actual_end: endIso,
    },
  };
}

function summarize(results: ResolveResult[]): string {
  const count = (status: ResolveResult["status"]) =>
    results.filter((item) => item.status === status).length;
  const problems = results.filter(
    (item) => item.status === "conflict" || item.status === "invalid",
  );
  const summary = [
    `Confirmadas: ${count("confirmed")}.`,
    `No realizadas: ${count("not_occurred")}.`,
    `Sin cambios: ${count("unchanged")}.`,
  ].join(" ");
  if (problems.length === 0) {
    return summary;
  }
  const details = problems
    .map(
      (item) =>
        `${item.occurrence_date}: ${item.message ?? "No se pudo resolver."}`,
    )
    .join(" ");
  return `${summary} ${details}`;
}
