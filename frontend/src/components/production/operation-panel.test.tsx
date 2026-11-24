import { createElement, type ReactNode } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({
    href,
    children,
    ...props
  }: {
    href: string;
    children?: ReactNode;
  }) => createElement("a", { href, ...props }, children),
}));

import { OperationSection } from "./operation-panel";
import type { Operation } from "@/lib/operations";

const operation: Operation = {
  id: "op-1",
  vidriera_id: "vid-1",
  operation_type: "irrigation",
  operation_label: "Riego",
  occurred_at: "2024-06-01T18:00:00Z",
  cycle_id: null,
  notes: null,
  recorded_at: "2024-06-01T18:05:00Z",
  updated_at: "2024-06-01T18:05:00Z",
  origin: "manual",
  interval_start: null,
  interval_end: null,
  timing_basis: null,
};

describe("OperationSection", () => {
  it("offers registration and an empty state", () => {
    const html = renderToStaticMarkup(
      <OperationSection vidrieraId="vid-1" operations={[]} />,
    );
    expect(html).toContain("Registrar operación");
    expect(html).toContain("Todavía no hay operaciones.");
    expect(html).toContain("/produccion/vidrieras/vid-1/operaciones/nueva");
  });

  it("lists a saved operation and marks the missing cycle", () => {
    const html = renderToStaticMarkup(
      <OperationSection vidrieraId="vid-1" operations={[operation]} />,
    );
    expect(html).toContain("Riego");
    expect(html).toContain("Sin ciclo");
    expect(html).toContain('href="/produccion/operaciones/op-1"');
  });

  it("shows a backend error", () => {
    const html = renderToStaticMarkup(
      <OperationSection
        vidrieraId="vid-1"
        operations={null}
        loadError="No se pudo consultar el servicio."
      />,
    );
    expect(html).toContain("No se pudo consultar el servicio.");
  });
});
