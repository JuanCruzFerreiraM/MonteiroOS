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

import { createOperation, updateOperation } from "./operation-actions";

function form(entries: Record<string, string>): FormData {
  const data = new FormData();
  for (const [key, value] of Object.entries(entries)) {
    data.set(key, value);
  }
  return data;
}

describe("operation actions", () => {
  beforeEach(() => {
    backendFetch.mockReset();
  });

  it("rejects an incomplete interval before calling the API", async () => {
    const result = await createOperation(
      {},
      form({
        vidriera_id: "vid-1",
        operation_type: "black_nylon",
        occurred_at: "2024-06-01T18:00",
        interval_start: "2024-06-01T18:00",
        cycle_id: "",
      }),
    );

    expect(result.error).toMatch(/inicio y fin/);
    expect(backendFetch).not.toHaveBeenCalled();
  });

  it("sends no cycle when the operator clears the default", async () => {
    backendFetch.mockResolvedValue(
      new Response(JSON.stringify({ id: "op-1" }), { status: 201 }),
    );

    await expect(
      createOperation(
        {},
        form({
          vidriera_id: "vid-1",
          operation_type: "irrigation",
          occurred_at: "2024-06-01T15:00",
          cycle_id: "",
          notes: "  ",
        }),
      ),
    ).rejects.toThrow("REDIRECT:/produccion/vidrieras/vid-1");

    const body = JSON.parse(String(backendFetch.mock.calls[0][1].body));
    expect(body.cycle_id).toBeNull();
    expect(body.notes).toBeNull();
    expect(body.vidriera_id).toBeUndefined();
  });

  it("returns the backend error and does not change the vidriera", async () => {
    backendFetch.mockResolvedValue(
      new Response(
        JSON.stringify({ detail: "El ciclo no pertenece a esta vidriera." }),
        { status: 422 },
      ),
    );

    const result = await updateOperation(
      {},
      form({
        operation_id: "op-1",
        vidriera_id: "vid-9",
        operation_type: "observation",
        occurred_at: "2024-06-03T11:00",
        cycle_id: "cycle-1",
      }),
    );

    const body = JSON.parse(String(backendFetch.mock.calls[0][1].body));
    expect(result.error).toMatch(/vidriera/);
    expect(body.vidriera_id).toBeUndefined();
    expect(body.operation_type).toBe("observation");
  });

  it("sends the actual start as the occurrence time of a scheduled operation", async () => {
    backendFetch.mockResolvedValue(
      new Response(JSON.stringify({ id: "op-1" }), { status: 200 }),
    );

    await expect(
      updateOperation(
        {},
        form({
          operation_id: "op-1",
          origin: "scheduled",
          operation_type: "irrigation",
          interval_start: "2024-06-01T18:30",
          interval_end: "2024-06-02T07:45",
          cycle_id: "",
        }),
      ),
    ).rejects.toThrow("REDIRECT:/produccion/operaciones/op-1");

    const body = JSON.parse(String(backendFetch.mock.calls[0][1].body));
    expect(body.operation_type).toBeUndefined();
    expect(body.occurred_at).toBe("2024-06-01T18:30:00-03:00");
    expect(body.interval_start).toBe(body.occurred_at);
    expect(body.interval_end).toBe("2024-06-02T07:45:00-03:00");
  });
});
