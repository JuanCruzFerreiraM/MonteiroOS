import { describe, expect, it } from "vitest";

import {
  closingDateError,
  cycleLabelMap,
  cycleOptionLabel,
  cycleStatusLabel,
  formatCycleDate,
  isCalendarDate,
  plantingDateError,
  suggestedClosingDate,
  type CultivationCycle,
} from "./cycles";

describe("calendar dates", () => {
  it("formats a planting date without shifting the day", () => {
    expect(formatCycleDate("2024-09-15")).toBe("15/09/2024");
    expect(isCalendarDate("2024-02-31")).toBe(false);
    expect(plantingDateError("2024-13-01")).toMatch(/AAAA-MM-DD/);
    expect(plantingDateError("2024-09-15")).toBeNull();
  });

  it("rejects a closing date before planting until the operator confirms", () => {
    expect(closingDateError("2024-03-02", "2024-03-01", true)).toMatch(
      /anterior/,
    );
    expect(closingDateError("2024-03-02", "2024-03-02", false)).toMatch(
      /Confirme/,
    );
    expect(closingDateError("2024-03-02", "2024-03-02", true)).toBeNull();
  });

  it("labels an active cycle and a finalized one separately", () => {
    const active: CultivationCycle = {
      id: "cycle-active",
      vidriera_id: "vid-1",
      start_date: "2024-06-01",
      end_date: null,
      status: "active",
      notes: null,
    };
    const finalized: CultivationCycle = {
      ...active,
      id: "cycle-old",
      start_date: "2024-01-01",
      end_date: "2024-03-01",
      status: "finalized",
    };
    expect(cycleOptionLabel(active)).toBe("Activo · 01/06/2024");
    expect(cycleLabelMap({ active, history: [finalized] })["cycle-old"]).toBe(
      "Finalizado · 01/01/2024 – 01/03/2024",
    );
  });

  it("suggests the calendar date in Argentina", () => {
    expect(suggestedClosingDate(new Date("2024-03-01T02:30:00Z"))).toBe(
      "2024-02-29",
    );
    expect(suggestedClosingDate(new Date("2024-03-01T04:00:00Z"))).toBe(
      "2024-03-01",
    );
    expect(cycleStatusLabel("active")).toBe("Activo");
    expect(cycleStatusLabel("finalized")).toBe("Finalizado");
  });
});
