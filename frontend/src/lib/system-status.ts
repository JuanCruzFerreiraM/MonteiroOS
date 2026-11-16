export type SystemStatus =
  | { state: "ok" }
  | { state: "database_unavailable" }
  | { state: "backend_unavailable" }
  | { state: "access_denied" };

export function interpretHealth(status: number, body: unknown): SystemStatus {
  if (status === 401 || status === 403) {
    return { state: "access_denied" };
  }
  if (status === 503) {
    return { state: "database_unavailable" };
  }
  if (
    status === 200 &&
    typeof body === "object" &&
    body !== null &&
    "status" in body &&
    body.status === "ok"
  ) {
    return { state: "ok" };
  }
  return { state: "backend_unavailable" };
}

export async function readSystemStatus(
  fetchImpl: typeof fetch = fetch,
): Promise<SystemStatus> {
  const base = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";
  const headers = new Headers();
  const secret = process.env.APP_ACCESS_SECRET?.trim();
  if (secret) {
    headers.set("X-Monteiro-Access", secret);
  }

  try {
    const response = await fetchImpl(`${base.replace(/\/$/, "")}/health`, {
      cache: "no-store",
      headers,
      signal: AbortSignal.timeout(3000),
    });
    const body: unknown = await response.json().catch(() => null);
    return interpretHealth(response.status, body);
  } catch {
    return { state: "backend_unavailable" };
  }
}
