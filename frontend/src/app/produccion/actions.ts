"use server";

import { unstable_rethrow } from "next/navigation";
import { redirect } from "next/navigation";

import { backendFetch, optionalText, readApiError } from "@/lib/backend";
import type { FormState, Quinta, VidrieraDetail } from "@/lib/production";

export async function createQuinta(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  return saveAndRedirect(
    "/api/production/quintas",
    "POST",
    {
      code: String(formData.get("code") ?? ""),
      name: String(formData.get("name") ?? ""),
      notes: optionalText(formData.get("notes")),
    },
    (created) =>
      `/produccion/quintas/${(created as Quinta).id}/mapa?paso=limite`,
  );
}

export async function updateQuinta(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  const id = String(formData.get("id") ?? "");
  return saveAndRedirect(
    `/api/production/quintas/${id}`,
    "PATCH",
    {
      name: String(formData.get("name") ?? ""),
      notes: optionalText(formData.get("notes")),
    },
    () => `/produccion/quintas/${id}`,
  );
}

export async function setQuintaActive(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  const id = String(formData.get("id") ?? "");
  const active = formData.get("active") === "true";
  return saveAndRedirect(
    `/api/production/quintas/${id}`,
    "PATCH",
    { active },
    () => `/produccion/quintas/${id}`,
  );
}

export async function createVidriera(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  const quintaId = String(formData.get("quinta_id") ?? "");
  return saveAndRedirect(
    `/api/production/quintas/${quintaId}/vidrieras`,
    "POST",
    {
      code: String(formData.get("code") ?? ""),
      name: String(formData.get("name") ?? ""),
      notes: optionalText(formData.get("notes")),
    },
    (created) => `/produccion/vidrieras/${(created as VidrieraDetail).id}`,
  );
}

export async function updateVidriera(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  const id = String(formData.get("id") ?? "");
  return saveAndRedirect(
    `/api/production/vidrieras/${id}`,
    "PATCH",
    {
      name: String(formData.get("name") ?? ""),
      notes: optionalText(formData.get("notes")),
    },
    () => `/produccion/vidrieras/${id}`,
  );
}

export async function setVidrieraActive(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  const id = String(formData.get("id") ?? "");
  const active = formData.get("active") === "true";
  return saveAndRedirect(
    `/api/production/vidrieras/${id}`,
    "PATCH",
    { active },
    () => `/produccion/vidrieras/${id}`,
  );
}

export async function updateCantero(
  _state: FormState,
  formData: FormData,
): Promise<FormState> {
  const id = String(formData.get("id") ?? "");
  const vidrieraId = String(formData.get("vidriera_id") ?? "");
  const name = optionalText(formData.get("name"));
  return saveAndRedirect(
    `/api/production/canteros/${id}`,
    "PATCH",
    {
      name,
      active: formData.get("active") === "on",
    },
    () => `/produccion/vidrieras/${vidrieraId}`,
  );
}

async function saveAndRedirect(
  path: string,
  method: "POST" | "PATCH",
  body: unknown,
  location: (created: unknown) => string,
): Promise<FormState> {
  try {
    const response = await backendFetch(path, {
      method,
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      return { error: await readApiError(response) };
    }
    const created: unknown = await response.json();
    redirect(location(created));
  } catch (error) {
    unstable_rethrow(error);
    return { error: "No se pudo completar la operación." };
  }
}
