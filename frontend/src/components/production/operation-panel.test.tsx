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

import {
  HistoryFilters,
  OperationHistory,
  OperationSection,
  historyPageHref,
} from "./operation-panel";
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
  resolution_id: null,
};

describe("OperationSection", () => {
  it("offers registration and an empty state", () => {
    const html = renderToStaticMarkup(
      <OperationSection vidrieraId="vid-1" operations={[]} />,
    );
    expect(html).toContain("Registrar operación");
    expect(html).toContain("Todavía no hay operaciones.");
    expect(html).toContain("/produccion/vidrieras/vid-1/operaciones/nueva");
    expect(html).toContain("/produccion/vidrieras/vid-1/historial");
  });

  it("lists a saved operation and marks the missing cycle", () => {
    const html = renderToStaticMarkup(
      <OperationSection vidrieraId="vid-1" operations={[operation]} />,
    );
    expect(html).toContain("Riego");
    expect(html).toContain("Sin ciclo");
    expect(html).toContain("Registro manual");
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

describe("operation history", () => {
  it("shows a confirmed interval and keeps an empty filter result distinct", () => {
    const saved = renderToStaticMarkup(
      <OperationHistory
        operations={[
          {
            ...operation,
            id: "op-light",
            operation_type: "artificial_lighting",
            operation_label: "Iluminación artificial",
            origin: "scheduled",
            notes: "timer revisado",
            interval_start: "2024-06-01T21:30:00Z",
            interval_end: "2024-06-02T04:45:00Z",
            timing_basis: "operator_entered",
            resolution_id: "res-1",
            cycle_id: "cycle-1",
          },
        ]}
        cycleLabels={{ "cycle-1": "Finalizado · 01/03/2024" }}
      />,
    );
    const empty = renderToStaticMarkup(
      <OperationHistory
        operations={[]}
        emptyMessage="Ninguna operación coincide con el filtro."
      />,
    );

    expect(saved).toContain("Confirmada desde la programación");
    expect(saved).toContain("timer revisado");
    expect(saved).toContain("Intervalo real:");
    expect(saved).toContain("Finalizado · 01/03/2024");
    expect(saved).toContain('href="/produccion/operaciones/op-light"');
    expect(empty).toContain("Ninguna operación coincide con el filtro.");
    expect(empty).not.toContain("Registre la primera");
  });

  it("offers a reset only when a filter is active and keeps the next page", () => {
    const idle = renderToStaticMarkup(
      <HistoryFilters vidrieraId="vid-1" cycles={[]} />,
    );
    const active = renderToStaticMarkup(
      <HistoryFilters
        vidrieraId="vid-1"
        type="irrigation"
        cycles={[{ id: "cycle-1", label: "Activo · 01/06/2024" }]}
      />,
    );

    expect(idle).toContain("Sin ciclo");
    expect(idle).not.toContain("Restablecer");
    expect(active).toContain("Restablecer");
    expect(active).toContain('href="/produccion/vidrieras/vid-1/historial"');
    expect(
      historyPageHref("vid-1", {
        type: "irrigation",
        cursor: "cursor-2",
      }),
    ).toBe(
      "/produccion/vidrieras/vid-1/historial?type=irrigation&cursor=cursor-2",
    );
  });
});
