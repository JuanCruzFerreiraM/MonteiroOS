"use server";

import { backendFetch, readApiError } from "@/lib/backend";
import type {
  Boundary,
  BoundaryWarning,
  GeoJsonPolygon,
} from "@/lib/production";

export type BoundarySaveResult =
  { ok: true; warnings: BoundaryWarning[] } | { ok: false; message: string };

export async function saveBoundary(
  kind: "quintas" | "vidrieras",
  id: string,
  geometry: GeoJsonPolygon,
  mode: "replace" | "attach",
): Promise<BoundarySaveResult> {
  try {
    const response = await backendFetch(
      `/api/production/${kind}/${id}/boundary`,
      {
        method: "PUT",
        body: JSON.stringify({ geometry, mode }),
      },
    );
    if (!response.ok) {
      return { ok: false, message: await readApiError(response) };
    }
    const body = (await response.json()) as Boundary;
    return { ok: true, warnings: body.warnings ?? [] };
  } catch {
    return { ok: false, message: "No se pudo guardar el límite." };
  }
}

export async function removeBoundary(
  kind: "quintas" | "vidrieras",
  id: string,
): Promise<{ ok: true } | { ok: false; message: string }> {
  try {
    const response = await backendFetch(
      `/api/production/${kind}/${id}/boundary`,
      {
        method: "DELETE",
      },
    );
    if (!response.ok) {
      return { ok: false, message: await readApiError(response) };
    }
    return { ok: true };
  } catch {
    return { ok: false, message: "No se pudo quitar el límite." };
  }
}

export async function loadNextVidrieraCode(
  quintaId: string,
): Promise<{ ok: true; code: string } | { ok: false; message: string }> {
  try {
    const response = await backendFetch(
      `/api/production/quintas/${quintaId}/vidrieras/next-code`,
    );
    if (!response.ok) {
      return { ok: false, message: await readApiError(response) };
    }
    const body = (await response.json()) as { code?: string };
    if (!body.code) {
      return {
        ok: false,
        message: "No se pudo sugerir el código de la vidriera.",
      };
    }
    return { ok: true, code: body.code };
  } catch {
    return {
      ok: false,
      message: "No se pudo sugerir el código de la vidriera.",
    };
  }
}

export async function createVidrieraRecord(
  quintaId: string,
  code: string,
  name: string,
): Promise<
  { ok: true; id: string; code: string } | { ok: false; message: string }
> {
  try {
    const response = await backendFetch(
      `/api/production/quintas/${quintaId}/vidrieras`,
      {
        method: "POST",
        body: JSON.stringify({ code, name }),
      },
    );
    if (!response.ok) {
      return { ok: false, message: await readApiError(response) };
    }
    const body = (await response.json()) as { id?: string; code?: string };
    if (!body.id || !body.code) {
      return { ok: false, message: "La vidriera no se creó correctamente." };
    }
    return { ok: true, id: body.id, code: body.code };
  } catch {
    return { ok: false, message: "No se pudo crear la vidriera." };
  }
}
