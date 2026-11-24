import { describe, expect, it } from "vitest";

import {
  closingDateError,
  cycleStatusLabel,
  formatCycleDate,
  isCalendarDate,
  plantingDateError,
  suggestedClosingDate,
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
