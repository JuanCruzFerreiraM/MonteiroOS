import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  redirect: () => undefined,
  unstable_rethrow: () => undefined,
}));

vi.mock("@/components/submit-button", () => ({
  SubmitButton: ({ label }: { label: string }) =>
    createElement("button", { type: "submit" }, label),
}));

import type { Operation } from "@/lib/operations";

import { OperationCreateForm, OperationEditForm } from "./operation-forms";

const scheduled: Operation = {
  id: "op-scheduled",
  vidriera_id: "vid-1",
  operation_type: "black_nylon",
  operation_label: "Cobertura con nylon negro",
  occurred_at: "2024-06-01T21:00:00Z",
  cycle_id: null,
  notes: null,
  recorded_at: "2024-06-02T12:00:00Z",
  updated_at: "2024-06-02T12:00:00Z",
  origin: "scheduled",
  interval_start: "2024-06-01T21:00:00Z",
  interval_end: "2024-06-02T11:00:00Z",
  timing_basis: "assumed_from_schedule",
  resolution_id: "res-1",
};

describe("OperationCreateForm", () => {
  it("selects the active cycle and offers an explicit empty choice", () => {
    const html = renderToStaticMarkup(
      <OperationCreateForm
        vidrieraId="vid-1"
        defaultCycleId="cycle-active"
        cycles={[
          { id: "cycle-active", label: "Activo · 01/06/2024" },
          { id: "cycle-old", label: "Finalizado · 01/03/2024" },
        ]}
      />,
    );

    expect(html).toContain("Sin ciclo");
    expect(html).toContain('value="cycle-active" selected=""');
    expect(html).not.toContain("interval_start");
  });

  it("shows an optional interval for lighting and keeps no cycle selected", () => {
    const html = renderToStaticMarkup(
      <OperationCreateForm
        vidrieraId="vid-1"
        defaultCycleId={null}
        cycles={[]}
        initialType="artificial_lighting"
      />,
    );
    expect(html).toContain("Inicio real");
    expect(html).toContain("Fin real");
    expect(html).not.toContain('name="interval_start" required');
    expect(html).toContain('value="" selected=""');
  });
});

describe("OperationEditForm", () => {
  it("keeps the type of a scheduled operation out of the editable choices", () => {
    const html = renderToStaticMarkup(
      <OperationEditForm operation={scheduled} cycles={[]} />,
    );

    expect(html).toContain("Cobertura con nylon negro");
    expect(html).toContain('name="origin" value="scheduled"');
    expect(html).not.toContain('name="operation_type"');
    expect(html).not.toContain('name="occurred_at"');
    expect(html).toContain("Inicio real");
    expect(html).toContain("required");
  });

  it("still lets a manual operation change its type", () => {
    const html = renderToStaticMarkup(
      <OperationEditForm
        operation={{
          ...scheduled,
          id: "op-manual",
          origin: "manual",
          operation_type: "irrigation",
          operation_label: "Riego",
          interval_start: null,
          interval_end: null,
          timing_basis: null,
          resolution_id: null,
        }}
        cycles={[]}
      />,
    );

    expect(html).toContain('name="operation_type"');
    expect(html).toContain('name="occurred_at"');
    expect(html).not.toContain('name="origin"');
  });
});
