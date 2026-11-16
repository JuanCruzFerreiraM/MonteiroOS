import { describe, expect, it, vi } from "vitest";

import { interpretHealth, readSystemStatus } from "./system-status";

describe("interpretHealth", () => {
  it("accepts a healthy payload", () => {
    expect(interpretHealth(200, { status: "ok" })).toEqual({ state: "ok" });
  });

  it("does not treat a database failure as an empty result", () => {
    expect(interpretHealth(503, { detail: "database unavailable" })).toEqual({
      state: "database_unavailable",
    });
  });

  it("reports access denial separately from a missing backend", () => {
    expect(interpretHealth(401, { detail: "access denied" })).toEqual({
      state: "access_denied",
    });
    expect(interpretHealth(500, null)).toEqual({
      state: "backend_unavailable",
    });
  });
});

describe("readSystemStatus", () => {
  it("returns backend_unavailable when the request fails", async () => {
    const fetchImpl = vi.fn(async () => {
      throw new Error("connection refused");
    });

    await expect(readSystemStatus(fetchImpl)).resolves.toEqual({
      state: "backend_unavailable",
    });
  });
});
