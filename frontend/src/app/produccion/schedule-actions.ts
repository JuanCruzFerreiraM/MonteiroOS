"use server";

import { redirect, unstable_rethrow } from "next/navigation";

import { backendFetch, optionalText, readApiError } from "@/lib/backend";
import { scheduleError } from "@/lib/schedules";
import type { FormState } from "@/lib/production";

export async function createSchedule(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  const vidrieraId = String(formData.get("vidriera_id") ?? "");
  const invalid = validateSchedule(formData);
  if (invalid) {
    return { error: invalid };
  }
  const response = await save(
    `/api/operations/vidrieras/${vidrieraId}/schedules`,
    "POST",
    scheduleBody(formData, true),
  );
  if (response.error) {
    return response;
  }
  redirect(`/produccion/vidrieras/${vidrieraId}/programacion`);
}

export async function reviseSchedule(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  const seriesId = String(formData.get("series_id") ?? "");
  const invalid = validateSchedule(formData);
  if (invalid) {
    return { error: invalid };
  }
  const response = await save(
    `/api/operations/schedules/${seriesId}/revisions`,
    "POST",
    {
      effective_from: String(formData.get("effective_from") ?? ""),
      ...scheduleBody(formData, false),
    },
  );
  if (response.error) {
    return response;
  }
  redirect(`/produccion/programacion/${seriesId}`);
}

export async function pauseSchedule(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  return changeLifecycle(formData, "pause");
}

export async function resumeSchedule(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  return changeLifecycle(formData, "resume");
}

export async function endSchedule(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  const seriesId = String(formData.get("series_id") ?? "");
  const response = await save(
    `/api/operations/schedules/${seriesId}/end`,
    "POST",
    {
      effective_end: String(formData.get("effective_end") ?? ""),
    },
  );
  if (response.error) {
    return response;
  }
  redirect(`/produccion/programacion/${seriesId}`);
}

function validateSchedule(formData: FormData): string | null {
  return scheduleError({
    start: String(
      formData.get("effective_start") || formData.get("effective_from") || "",
    ),
    end: String(formData.get("effective_end") ?? ""),
    weekdays: formData
      .getAll("weekdays")
      .map((value) => Number(value))
      .filter((value) => Number.isInteger(value)),
    startTime: String(formData.get("start_time") ?? ""),
    endTime: String(formData.get("end_time") ?? ""),
  });
}

function scheduleBody(
  formData: FormData,
  creating: boolean,
): Record<string, unknown> {
  const weekdays = formData
    .getAll("weekdays")
    .map((value) => Number(value))
    .filter((value) => Number.isInteger(value));
  const body: Record<string, unknown> = {
    effective_end: String(formData.get("effective_end") ?? ""),
    weekdays,
    start_time: String(formData.get("start_time") ?? ""),
    end_time: String(formData.get("end_time") ?? ""),
    notes: optionalText(formData.get("notes")),
  };
  if (creating) {
    body.operation_type = String(formData.get("operation_type") ?? "");
    body.effective_start = String(formData.get("effective_start") ?? "");
  }
  return body;
}

async function changeLifecycle(
  formData: FormData,
  action: "pause" | "resume",
): Promise<FormState> {
  const seriesId = String(formData.get("series_id") ?? "");
  const response = await save(
    `/api/operations/schedules/${seriesId}/${action}`,
    "POST",
    { effective_from: String(formData.get("effective_from") ?? "") },
  );
  if (response.error) {
    return response;
  }
  redirect(`/produccion/programacion/${seriesId}`);
}

async function save(
  path: string,
  method: "POST",
  body: unknown,
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
    return {};
  } catch (error) {
    unstable_rethrow(error);
    return { error: "No se pudo completar la operación." };
  }
}
