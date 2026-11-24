import { beforeEach, describe, expect, it, vi } from "vitest";

const backendFetch = vi.hoisted(() => vi.fn());
const revalidatePath = vi.hoisted(() => vi.fn());

vi.mock("next/cache", () => ({ revalidatePath }));
vi.mock("next/navigation", () => ({
  unstable_rethrow: () => undefined,
}));
vi.mock("@/lib/backend", async () => {
  const actual =
    await vi.importActual<typeof import("@/lib/backend")>("@/lib/backend");
  return { ...actual, backendFetch };
});

import { resolveOccurrences } from "./confirmation-actions";

function form(
  entries: Record<string, string>,
  occurrences: string[] = [],
): FormData {
  const data = new FormData();
  for (const [key, value] of Object.entries(entries)) {
    data.set(key, value);
  }
  for (const value of occurrences) {
    data.append("occurrence", value);
  }
  return data;
}

describe("confirmation actions", () => {
  beforeEach(() => {
    backendFetch.mockReset();
    revalidatePath.mockReset();
  });

  it("asks for a selection before calling the API", async () => {
    const result = await resolveOccurrences(
      {},
      form({ vidriera_id: "vid-1", outcome: "confirmed" }),
    );
    expect(result.error).toMatch(/Seleccione/);
    expect(backendFetch).not.toHaveBeenCalled();
  });

  it("confirms a batch with the scheduled interval as an assumption", async () => {
    backendFetch.mockResolvedValue(
      new Response(
        JSON.stringify([
          { occurrence_date: "2024-06-01", status: "confirmed", message: null },
          {
            occurrence_date: "2024-06-02",
            status: "conflict",
            message: "Ya resuelta.",
          },
        ]),
        { status: 200 },
      ),
    );
    const result = await resolveOccurrences(
      {},
      form({ vidriera_id: "vid-1", outcome: "confirmed" }, [
        "series-1|2024-06-01|2024-06-02T01:00:00Z|2024-06-02T05:00:00Z",
        "series-1|2024-06-02|2024-06-03T01:00:00Z|2024-06-03T05:00:00Z",
      ]),
    );
    const body = JSON.parse(String(backendFetch.mock.calls[0][1].body));
    expect(body.items).toHaveLength(2);
    expect(body.items[0].timing_basis).toBe("assumed_from_schedule");
    expect(body.items[0].actual_start).toBeUndefined();
    expect(body.items[0].cycle_id).toBeUndefined();
    expect(result.notice).toMatch(/Confirmadas: 1/);
    expect(result.notice).toMatch(/Ya resuelta/);
  });

  it("sends operator times when a single interval differs from the schedule", async () => {
    backendFetch.mockResolvedValue(
      new Response(
        JSON.stringify([
          { occurrence_date: "2024-06-01", status: "confirmed", message: null },
        ]),
        { status: 200 },
      ),
    );
    await resolveOccurrences(
      {},
      form(
        {
          vidriera_id: "vid-1",
          outcome: "confirmed",
          actual_start: "2024-06-01T18:30",
          actual_end: "2024-06-02T07:45",
          cycle_id: "",
        },
        ["series-1|2024-06-01|2024-06-01T21:00:00Z|2024-06-02T11:00:00Z"],
      ),
    );
    const body = JSON.parse(String(backendFetch.mock.calls[0][1].body));
    expect(body.items[0].timing_basis).toBe("operator_entered");
    expect(body.items[0].actual_start).toBe("2024-06-01T18:30:00-03:00");
    expect(body.items[0].actual_end).toBe("2024-06-02T07:45:00-03:00");
    expect(body.items[0].cycle_id).toBeNull();
  });
});
