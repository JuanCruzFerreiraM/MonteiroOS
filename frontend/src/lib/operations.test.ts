import { describe, expect, it } from "vitest";

import {
  acceptsInterval,
  formatOccurredAt,
  fromLocalInput,
  intervalError,
  occurredAtError,
  operationLabel,
  toLocalInput,
} from "./operations";

describe("operation times", () => {
  it("labels the catalog in Spanish and limits intervals", () => {
    expect(operationLabel("black_nylon")).toBe("Cobertura con nylon negro");
    expect(acceptsInterval("irrigation")).toBe(false);
    expect(acceptsInterval("artificial_lighting")).toBe(true);
  });

  it("keeps Argentina civil time when converting an instant", () => {
    expect(toLocalInput("2024-06-02T01:00:00Z")).toBe("2024-06-01T22:00");
    expect(fromLocalInput("2024-06-01T22:00")).toBe(
      "2024-06-01T22:00:00-03:00",
    );
    expect(occurredAtError("2024-06-01")).toMatch(/válidas/);
    expect(formatOccurredAt("2024-06-02T05:00:00Z")).toContain("02:00");
    expect(formatOccurredAt("2024-06-02T05:00:00Z")).toContain("02/06/2024");
  });

  it("requires a completed interval and allows overnight coverage", () => {
    expect(intervalError("", "2024-06-02T02:00")).toMatch(/inicio y fin/);
    expect(intervalError("2024-06-02T08:00", "2024-06-01T18:00")).toMatch(
      /posterior/,
    );
    expect(intervalError("2024-06-01T22:00", "2024-06-02T02:00")).toBeNull();
  });
});
