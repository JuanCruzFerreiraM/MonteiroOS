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

import { OperationCreateForm } from "./operation-forms";

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
