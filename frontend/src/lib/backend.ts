import type { FormState } from "./production";

export function buildAccessHeaders(secret: string | undefined): Headers {
  const headers = new Headers();
  const trimmed = secret?.trim();
  if (trimmed) {
    headers.set("X-Monteiro-Access", trimmed);
  }
  return headers;
}

export function backendBaseUrl(configured: string | undefined): string {
  const base = configured?.trim() || "http://127.0.0.1:8000";
  return base.replace(/\/$/, "");
}

export async function readApiError(response: Response): Promise<string> {
  const body: unknown = await response.json().catch(() => null);
  if (typeof body === "object" && body !== null && "detail" in body) {
    const detail = body.detail;
    if (typeof detail === "string" && detail.trim()) {
      return detail;
    }
    if (Array.isArray(detail)) {
      const first = detail.find(
        (item) =>
          typeof item === "object" &&
          item !== null &&
          "msg" in item &&
          typeof item.msg === "string",
      );
      if (
        first &&
        typeof first === "object" &&
        "msg" in first &&
        typeof first.msg === "string"
      ) {
        return first.msg;
      }
    }
  }
  return "No se pudo completar la operación.";
}

export async function backendFetch(
  path: string,
  init?: RequestInit,
): Promise<Response> {
  if (typeof window !== "undefined") {
    throw new Error("La API se consulta solo desde el servidor.");
  }
  const headers = buildAccessHeaders(process.env.APP_ACCESS_SECRET);
  new Headers(init?.headers).forEach((value, key) => {
    headers.set(key, value);
  });
  if (init?.body !== undefined && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  return fetch(`${backendBaseUrl(process.env.BACKEND_URL)}${path}`, {
    ...init,
    headers,
    cache: "no-store",
    signal: init?.signal ?? AbortSignal.timeout(8000),
  });
}

export async function readJson<T>(path: string): Promise<
  | { ok: true; data: T }
  | {
      ok: false;
      status: number;
      message: string;
    }
> {
  try {
    const response = await backendFetch(path);
    if (!response.ok) {
      return {
        ok: false,
        status: response.status,
        message: await readApiError(response),
      };
    }
    return { ok: true, data: (await response.json()) as T };
  } catch {
    return {
      ok: false,
      status: 0,
      message: "No se pudo consultar el servicio.",
    };
  }
}

export function formError(error: unknown): FormState {
  if (error instanceof Error && error.message) {
    return { error: error.message };
  }
  return { error: "No se pudo completar la operación." };
}

export function optionalText(value: FormDataEntryValue | null): string | null {
  if (typeof value !== "string") {
    return null;
  }
  const trimmed = value.trim();
  return trimmed ? value : null;
}
