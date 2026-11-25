import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/cache", () => ({ revalidatePath: () => undefined }));
vi.mock("next/navigation", () => ({ unstable_rethrow: () => undefined }));

import { OccurrenceBoard } from "./occurrence-board";
import type { Occurrence } from "@/lib/schedules";

function occurrence(status: Occurrence["status"], date: string): Occurrence {
  return {
    series_id: "series-1",
    revision_id: "rev-1",
    vidriera_id: "vid-1",
    occurrence_date: date,
    operation_type: "black_nylon",
    operation_label: "Cobertura con nylon negro",
    status,
    expected_start: "2024-06-01T21:00:00Z",
    expected_end: "2024-06-02T11:00:00Z",
    actual_start: status === "confirmed" ? "2024-06-01T21:30:00Z" : null,
    actual_end: status === "confirmed" ? "2024-06-02T10:45:00Z" : null,
    timing_basis: status === "confirmed" ? "operator_entered" : null,
    confirmation_method: status === "confirmed" ? "manual" : null,
    suggested_cycle_id: "cycle-1",
    cycle_id: null,
    operation_id: status === "confirmed" ? "op-1" : null,
    notes: null,
  };
}

describe("OccurrenceBoard", () => {
  it("shows an empty period", () => {
    const html = renderToStaticMarkup(
      <OccurrenceBoard vidrieraId="vid-1" occurrences={[]} cycles={[]} />,
    );
    expect(html).toContain("No hay ocurrencias en este período.");
  });

  it("lets unverified rows be selected and keeps future rows distinct", () => {
    const html = renderToStaticMarkup(
      <OccurrenceBoard
        vidrieraId="vid-1"
        cycles={[{ id: "cycle-1", label: "Activo · 01/06/2024" }]}
        occurrences={[
          occurrence("scheduled", "2026-12-01"),
          occurrence("unverified", "2024-06-01"),
          occurrence("confirmed", "2024-05-31"),
        ]}
      />,
    );
    expect(html).toContain("Programada");
    expect(html).toContain("Pendiente de verificación");
    expect(html).toContain("Confirmada");
    expect(html.match(/type="checkbox"/g)).toHaveLength(1);
    expect(html).toContain("No hay ocurrencias elegidas.");
    expect(html).toContain("Real ");
  });
});
