import { describe, expect, it } from "vitest";

import { buildAccessHeaders, backendBaseUrl, readApiError } from "./backend";

describe("backend access", () => {
  it("sends the deployment secret only when it is configured", () => {
    const headers = buildAccessHeaders("  secreto  ");

    expect(headers.get("X-Monteiro-Access")).toBe("secreto");
    expect(buildAccessHeaders("   ").has("X-Monteiro-Access")).toBe(false);
    expect(buildAccessHeaders(undefined).has("X-Monteiro-Access")).toBe(false);
  });

  it("uses the server backend address", () => {
    expect(backendBaseUrl("http://backend:8000/")).toBe("http://backend:8000");
    expect(backendBaseUrl(undefined)).toBe("http://127.0.0.1:8000");
  });

  it("reads a readable API error", async () => {
    const response = new Response(
      JSON.stringify({ detail: "Ya existe una quinta con ese código." }),
      { status: 409 },
    );

    await expect(readApiError(response)).resolves.toBe(
      "Ya existe una quinta con ese código.",
    );
  });
});
