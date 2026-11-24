import { describe, expect, it } from "vitest";

import {
  addDays,
  occurrenceStatusLabel,
  scheduleError,
  weekdayLabels,
} from "./schedules";

describe("schedule helpers", () => {
  it("keeps calendar days and weekday labels", () => {
    expect(addDays("2024-06-01", 10)).toBe("2024-06-11");
    expect(weekdayLabels([7, 1])).toBe("Lunes, Domingo");
    expect(occurrenceStatusLabel("unverified")).toBe(
      "Pendiente de verificación",
    );
    expect(occurrenceStatusLabel("scheduled")).toBe("Programada");
  });

  it("rejects an empty week and equal times, and allows overnight", () => {
    expect(
      scheduleError({
        start: "2024-06-10",
        end: "2024-06-01",
        weekdays: [1],
        startTime: "22:00",
        endTime: "02:00",
      }),
    ).toMatch(/anterior/);
    expect(
      scheduleError({
        start: "2024-06-01",
        end: "2024-06-20",
        weekdays: [],
        startTime: "22:00",
        endTime: "02:00",
      }),
    ).toMatch(/día/);
    expect(
      scheduleError({
        start: "2024-06-01",
        end: "2024-06-20",
        weekdays: [1, 2, 3, 4, 5, 6, 7],
        startTime: "22:00",
        endTime: "22:00",
      }),
    ).toMatch(/iguales/);
    expect(
      scheduleError({
        start: "2024-12-01",
        end: "2024-12-20",
        weekdays: [1, 2, 3, 4, 5, 6, 7],
        startTime: "22:00",
        endTime: "02:00",
      }),
    ).toBeNull();
  });
});
