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

import { createSchedule, reviseSchedule } from "./schedule-actions";

function form(
  entries: Record<string, string>,
  weekdays: string[] = [],
): FormData {
  const data = new FormData();
  for (const [key, value] of Object.entries(entries)) {
    data.set(key, value);
  }
  for (const day of weekdays) {
    data.append("weekdays", day);
  }
  return data;
}

describe("schedule actions", () => {
  beforeEach(() => {
    backendFetch.mockReset();
  });

  it("rejects an empty week before calling the API", async () => {
    const result = await createSchedule(
      {},
      form({
        vidriera_id: "vid-1",
        operation_type: "artificial_lighting",
        effective_start: "2024-12-01",
        effective_end: "2024-12-20",
        start_time: "22:00",
        end_time: "02:00",
      }),
    );
    expect(result.error).toMatch(/día/);
    expect(backendFetch).not.toHaveBeenCalled();
  });

  it("creates a schedule and returns to the vidriera", async () => {
    backendFetch.mockResolvedValue(
      new Response(JSON.stringify({ series_id: "series-1" }), { status: 201 }),
    );
    await expect(
      createSchedule(
        {},
        form(
          {
            vidriera_id: "vid-1",
            operation_type: "black_nylon",
            effective_start: "2024-12-01",
            effective_end: "2024-12-20",
            start_time: "18:00",
            end_time: "08:00",
            notes: "  ",
          },
          ["1", "2", "3", "4", "5", "6", "7"],
        ),
      ),
    ).rejects.toThrow("REDIRECT:/produccion/vidrieras/vid-1/programacion");
    const body = JSON.parse(String(backendFetch.mock.calls[0][1].body));
    expect(body.operation_type).toBe("black_nylon");
    expect(body.weekdays).toEqual([1, 2, 3, 4, 5, 6, 7]);
    expect(body.notes).toBeNull();
    expect(body.effective_from).toBeUndefined();
  });

  it("revises from an effective date without sending a new start", async () => {
    backendFetch.mockResolvedValue(
      new Response(JSON.stringify({ series_id: "series-1" }), { status: 200 }),
    );
    await expect(
      reviseSchedule(
        {},
        form(
          {
            series_id: "series-1",
            effective_from: "2024-12-10",
            effective_end: "2024-12-20",
            start_time: "21:00",
            end_time: "03:00",
          },
          ["1"],
        ),
      ),
    ).rejects.toThrow("REDIRECT:/produccion/programacion/series-1");
    const body = JSON.parse(String(backendFetch.mock.calls[0][1].body));
    expect(body.effective_from).toBe("2024-12-10");
    expect(body.effective_start).toBeUndefined();
    expect(body.operation_type).toBeUndefined();
  });
});
