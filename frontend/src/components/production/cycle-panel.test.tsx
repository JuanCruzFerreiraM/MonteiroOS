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

vi.mock("next/navigation", () => ({
  redirect: vi.fn(),
  unstable_rethrow: vi.fn(),
}));

import { CycleSection } from "./cycle-panel";
import type { CultivationCycle } from "@/lib/cycles";

const active: CultivationCycle = {
  id: "cycle-1",
  vidriera_id: "vid-1",
  start_date: "2024-09-15",
  end_date: null,
  status: "active",
  notes: "Plantín del norte",
};

const previous: CultivationCycle = {
  id: "cycle-0",
  vidriera_id: "vid-1",
  start_date: "2023-08-01",
  end_date: "2024-01-20",
  status: "finalized",
  notes: null,
};

function markup(node: ReactNode): string {
  return renderToStaticMarkup(node);
}

describe("CycleSection", () => {
  it("offers a planting date when the vidriera has no cycle", () => {
    const html = markup(
      <CycleSection
        vidrieraId="vid-1"
        cycles={{ active: null, history: [] }}
        suggestedEndDate="2024-11-24"
      />,
    );

    expect(html).toContain("No hay un ciclo activo");
    expect(html).toContain("sin asignarse a un ciclo");
    expect(html).toContain("Fecha de plantación");
    expect(html).toContain("Iniciar ciclo");
    expect(html).not.toContain("Finalizar ciclo");
    expect(html).toContain("Todavía no hay ciclos finalizados.");
  });

  it("shows the active cycle and asks for an explicit closing date", () => {
    const html = markup(
      <CycleSection
        vidrieraId="vid-1"
        cycles={{ active, history: [] }}
        suggestedEndDate="2024-11-24"
      />,
    );

    expect(html).toContain("Activo");
    expect(html).toContain("15/09/2024");
    expect(html).toContain("Plantín del norte");
    expect(html).toContain('value="2024-11-24"');
    expect(html).toContain("Confirmo que este ciclo termina");
    expect(html).toContain("Finalizar ciclo");
    expect(html).toContain('href="/produccion/ciclos/cycle-1"');
    expect(html).not.toContain("Iniciar ciclo");
  });

  it("links each finalized cycle with both dates", () => {
    const html = markup(
      <CycleSection
        vidrieraId="vid-1"
        cycles={{ active, history: [previous] }}
        suggestedEndDate="2024-11-24"
      />,
    );

    expect(html).toContain('href="/produccion/ciclos/cycle-0"');
    expect(html).toContain("01/08/2023");
    expect(html).toContain("20/01/2024");
    expect(html).toContain("Finalizado");
  });

  it("shows a backend error without offering to start another cycle", () => {
    const html = markup(
      <CycleSection
        vidrieraId="vid-1"
        cycles={null}
        loadError="Esta vidriera ya tiene un ciclo activo desde 2024-01-15 (cycle-1)."
        suggestedEndDate="2024-11-24"
      />,
    );

    expect(html).toContain('role="alert"');
    expect(html).toContain("ya tiene un ciclo activo");
    expect(html).toContain("cycle-1");
    expect(html).not.toContain("Iniciar ciclo");
  });
});
