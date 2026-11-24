"use server";

import { redirect, unstable_rethrow } from "next/navigation";

import { backendFetch, optionalText, readApiError } from "@/lib/backend";
import {
  closingDateError,
  isCalendarDate,
  plantingDateError,
} from "@/lib/cycles";
import type { FormState } from "@/lib/production";

export async function startCycle(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  const vidrieraId = String(formData.get("vidriera_id") ?? "");
  const start = String(formData.get("start_date") ?? "");
  const invalid = plantingDateError(start);
  if (invalid) {
    return { error: invalid };
  }
  return save(
    `/api/production/vidrieras/${vidrieraId}/cycles`,
    "POST",
    {
      start_date: start,
      notes: optionalText(formData.get("notes")),
    },
    `/produccion/vidrieras/${vidrieraId}`,
  );
}

export async function finalizeCycle(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  const cycleId = String(formData.get("cycle_id") ?? "");
  const vidrieraId = String(formData.get("vidriera_id") ?? "");
  const start = String(formData.get("start_date") ?? "");
  const end = String(formData.get("end_date") ?? "");
  const invalid = closingDateError(
    start,
    end,
    formData.get("confirm") === "on",
  );
  if (invalid) {
    return { error: invalid };
  }
  return save(
    `/api/production/cycles/${cycleId}/finalize`,
    "POST",
    { end_date: end },
    `/produccion/vidrieras/${vidrieraId}`,
  );
}

export async function correctCycle(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  const cycleId = String(formData.get("cycle_id") ?? "");
  const start = String(formData.get("start_date") ?? "");
  const invalidStart = plantingDateError(start);
  if (invalidStart) {
    return { error: invalidStart };
  }
  const active = formData.get("status") === "active";
  const body: { start_date: string; end_date?: string; notes: string | null } =
    {
      start_date: start,
      notes: optionalText(formData.get("notes")),
    };
  if (!active) {
    const end = String(formData.get("end_date") ?? "");
    if (!isCalendarDate(end)) {
      return {
        error: "La fecha de cierre debe ser una fecha válida (AAAA-MM-DD).",
      };
    }
    if (end < start) {
      return {
        error: "La fecha de cierre no puede ser anterior a la plantación.",
      };
    }
    body.end_date = end;
  }
  return save(
    `/api/production/cycles/${cycleId}`,
    "PATCH",
    body,
    `/produccion/ciclos/${cycleId}`,
  );
}

async function save(
  path: string,
  method: "POST" | "PATCH",
  body: unknown,
  location: string,
): Promise<FormState> {
  try {
    const response = await backendFetch(path, {
      method,
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      return { error: await readApiError(response) };
    }
    await response.json();
    redirect(location);
  } catch (error) {
    unstable_rethrow(error);
    return { error: "No se pudo completar la operación." };
  }
}
