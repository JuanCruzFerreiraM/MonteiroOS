"use server";

import { redirect, unstable_rethrow } from "next/navigation";

import { backendFetch, optionalText, readApiError } from "@/lib/backend";
import {
  acceptsInterval,
  fromLocalInput,
  intervalError,
  occurredAtError,
} from "@/lib/operations";
import type { FormState } from "@/lib/production";

export async function createOperation(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  const vidrieraId = String(formData.get("vidriera_id") ?? "");
  const operationType = String(formData.get("operation_type") ?? "");
  const occurred = String(formData.get("occurred_at") ?? "");
  const invalid = occurredAtError(occurred);
  if (invalid) {
    return { error: invalid };
  }
  const body: Record<string, unknown> = {
    operation_type: operationType,
    occurred_at: fromLocalInput(occurred),
    cycle_id: optionalText(formData.get("cycle_id")),
    notes: optionalText(formData.get("notes")),
  };
  const interval = intervalPayload(operationType, formData);
  if (interval.error) {
    return { error: interval.error };
  }
  Object.assign(body, interval.fields);
  const response = await save(
    `/api/operations/vidrieras/${vidrieraId}/operations`,
    "POST",
    body,
  );
  if (response.error) {
    return response;
  }
  redirect(`/produccion/vidrieras/${vidrieraId}`);
}

export async function updateOperation(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  const operationId = String(formData.get("operation_id") ?? "");
  const scheduled = String(formData.get("origin") ?? "") === "scheduled";
  const operationType = String(formData.get("operation_type") ?? "");
  const body: Record<string, unknown> = {
    cycle_id: optionalText(formData.get("cycle_id")),
    notes: optionalText(formData.get("notes")),
  };
  if (scheduled) {
    const start = String(formData.get("interval_start") ?? "");
    const end = String(formData.get("interval_end") ?? "");
    if (!start || !end) {
      return { error: "El intervalo real necesita inicio y fin." };
    }
    const invalid = intervalError(start, end);
    if (invalid) {
      return { error: invalid };
    }
    const actualStart = fromLocalInput(start);
    body.occurred_at = actualStart;
    body.interval_start = actualStart;
    body.interval_end = fromLocalInput(end);
  } else {
    const occurred = String(formData.get("occurred_at") ?? "");
    const invalid = occurredAtError(occurred);
    if (invalid) {
      return { error: invalid };
    }
    body.operation_type = operationType;
    body.occurred_at = fromLocalInput(occurred);
    const interval = intervalPayload(operationType, formData);
    if (interval.error) {
      return { error: interval.error };
    }
    if (acceptsInterval(operationType)) {
      body.interval_start = interval.fields.interval_start ?? null;
      body.interval_end = interval.fields.interval_end ?? null;
    }
  }
  const response = await save(
    `/api/operations/operations/${operationId}`,
    "PATCH",
    body,
  );
  if (response.error) {
    return response;
  }
  redirect(`/produccion/operaciones/${operationId}`);
}

function intervalPayload(
  operationType: string,
  formData: FormData,
): { error?: string; fields: Record<string, string> } {
  if (!acceptsInterval(operationType)) {
    return { fields: {} };
  }
  const start = String(formData.get("interval_start") ?? "");
  const end = String(formData.get("interval_end") ?? "");
  const invalid = intervalError(start, end);
  if (invalid) {
    return { error: invalid, fields: {} };
  }
  if (!start && !end) {
    return { fields: {} };
  }
  return {
    fields: {
      interval_start: fromLocalInput(start) ?? "",
      interval_end: fromLocalInput(end) ?? "",
    },
  };
}

async function save(
  path: string,
  method: "POST" | "PATCH",
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
