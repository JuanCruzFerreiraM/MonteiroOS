import { beforeEach, describe, expect, it, vi } from "vitest";

const backendFetch = vi.hoisted(() => vi.fn());

vi.mock("next/navigation", () => ({
  redirect: (location: string) => {
    throw new Error(`REDIRECT:${location}`);
  },
  unstable_rethrow: (error: unknown) => {
    if (error instanceof Error && error.message.startsWith("REDIRECT:")) {
      throw error;
    }
  },
}));

vi.mock("@/lib/backend", async () => {
  const actual =
    await vi.importActual<typeof import("@/lib/backend")>("@/lib/backend");
  return { ...actual, backendFetch };
});

import { correctCycle, finalizeCycle, startCycle } from "./cycle-actions";

function form(entries: Record<string, string>): FormData {
  const data = new FormData();
  for (const [key, value] of Object.entries(entries)) {
    data.set(key, value);
  }
  return data;
}

function jsonResponse(status: number, detail: string): Response {
  return new Response(JSON.stringify({ detail }), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("cycle actions", () => {
  beforeEach(() => {
    backendFetch.mockReset();
  });

  it("rejects an invalid planting date before calling the API", async () => {
    const result = await startCycle(
      {},
      form({ vidriera_id: "vid-1", start_date: "2024-02-31" }),
    );

    expect(result.error).toMatch(/AAAA-MM-DD/);
    expect(backendFetch).not.toHaveBeenCalled();
  });

  it("returns the conflicting cycle reported by the API", async () => {
    backendFetch.mockResolvedValue(
      jsonResponse(
        409,
        "Esta vidriera ya tiene un ciclo activo desde 2024-01-15 (cycle-1).",
      ),
    );

    const result = await startCycle(
      {},
      form({ vidriera_id: "vid-1", start_date: "2024-06-01", notes: "  " }),
    );

    expect(result.error).toContain("cycle-1");
    expect(backendFetch).toHaveBeenCalledWith(
      "/api/production/vidrieras/vid-1/cycles",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ start_date: "2024-06-01", notes: null }),
      }),
    );
  });

  it("requires confirmation and a closing date on or after planting", async () => {
    const early = await finalizeCycle(
      {},
      form({
        cycle_id: "cycle-1",
        vidriera_id: "vid-1",
        start_date: "2024-03-02",
        end_date: "2024-03-01",
        confirm: "on",
      }),
    );
    const unconfirmed = await finalizeCycle(
      {},
      form({
        cycle_id: "cycle-1",
        vidriera_id: "vid-1",
        start_date: "2024-03-02",
        end_date: "2024-03-02",
      }),
    );

    expect(early.error).toMatch(/anterior/);
    expect(unconfirmed.error).toMatch(/Confirme/);
    expect(backendFetch).not.toHaveBeenCalled();
  });

  it("keeps an active cycle active and does not send another vidriera", async () => {
    backendFetch.mockResolvedValue(
      new Response(JSON.stringify({ id: "cycle-1" }), { status: 200 }),
    );

    await expect(
      correctCycle(
        {},
        form({
          cycle_id: "cycle-1",
          vidriera_id: "vid-9",
          status: "active",
          start_date: "2024-03-02",
          end_date: "2024-05-01",
          notes: "ajuste",
        }),
      ),
    ).rejects.toThrow("REDIRECT:/produccion/ciclos/cycle-1");

    const body = JSON.parse(String(backendFetch.mock.calls[0][1].body));
    expect(backendFetch.mock.calls[0][0]).toBe(
      "/api/production/cycles/cycle-1",
    );
    expect(body).toEqual({ start_date: "2024-03-02", notes: "ajuste" });
    expect(body.vidriera_id).toBeUndefined();
    expect(body.end_date).toBeUndefined();
  });

  it("rejects a finalized correction that ends before planting", async () => {
    const result = await correctCycle(
      {},
      form({
        cycle_id: "cycle-1",
        vidriera_id: "vid-1",
        status: "finalized",
        start_date: "2024-03-02",
        end_date: "2024-03-01",
      }),
    );

    expect(result.error).toMatch(/anterior/);
    expect(backendFetch).not.toHaveBeenCalled();
  });
});
