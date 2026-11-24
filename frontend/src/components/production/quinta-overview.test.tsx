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

vi.mock("@/app/produccion/forms", () => ({
  ActiveToggleForm: () => createElement("button", { type: "submit" }, "Estado"),
}));

vi.mock("@/components/map/farm-overview-loader", () => ({
  FarmOverviewLoader: ({
    mapData,
  }: {
    mapData: {
      name: string;
      vidrieras: Array<{ id: string; geometry: unknown }>;
    };
  }) =>
    createElement(
      "div",
      {
        role: "application",
        "aria-label": `Mapa de ${mapData.name}`,
        "data-polygons": mapData.vidrieras
          .filter((vidriera) => vidriera.geometry)
          .map((vidriera) => vidriera.id)
          .join(" "),
      },
      "mapa",
    ),
}));

import type { Quinta, QuintaMap, Vidriera } from "@/lib/production";
import { QuintaOverview } from "./quinta-overview";

const quinta: Quinta = {
  id: "q1",
  code: "VE",
  name: "Villa Elisa",
  notes: null,
  active: true,
};

const square = {
  type: "Polygon" as const,
  coordinates: [
    [
      [-58.1, -34.9],
      [-58.0, -34.9],
      [-58.0, -34.8],
      [-58.1, -34.9],
    ],
  ],
};

const mappedId = "11111111-1111-4111-8111-111111111111";
const unmappedId = "22222222-2222-4222-8222-222222222222";

const mapData: QuintaMap = {
  id: "q1",
  code: "VE",
  name: "Villa Elisa",
  active: true,
  geometry: square,
  vidrieras: [
    {
      id: mappedId,
      code: "VE-V001",
      name: "Norte",
      active: true,
      geometry: square,
      warnings: [],
    },
    {
      id: unmappedId,
      code: "VE-V002",
      name: "Sur",
      active: true,
      geometry: null,
      warnings: [],
    },
  ],
};

const vidrieras: Vidriera[] = [
  {
    id: mappedId,
    quinta_id: "q1",
    code: "VE-V001",
    name: "Norte",
    notes: null,
    active: true,
  },
  {
    id: unmappedId,
    quinta_id: "q1",
    code: "VE-V002",
    name: "Sur",
    notes: null,
    active: true,
  },
];

describe("quinta overview", () => {
  it("shows the map, the saved vidriera polygon, and the unmapped vidriera", () => {
    const html = renderToStaticMarkup(
      createElement(QuintaOverview, {
        quinta,
        map: mapData,
        mapFailed: false,
        vidrieras,
        vidrierasMessage: null,
        includeInactive: false,
      }),
    );

    expect(html).toContain('aria-label="Mapa de Villa Elisa"');
    expect(html).toContain(`data-polygons="${mappedId}"`);
    expect(html).not.toContain(`data-polygons="${unmappedId}"`);
    expect(html).toContain(`href="/produccion/vidrieras/${unmappedId}"`);
    expect(html).toContain(`href="/produccion/vidrieras/${mappedId}"`);
    expect(html).toContain('href="/produccion/quintas/q1/mapa"');
    expect(html).toContain("Editar mapa");
    expect(html).toContain("Editar datos");
    expect(html).toContain("Crear vidriera");
    expect(html).toContain("huella aproximada");
  });

  it("offers a way to locate a quinta that has no boundary", () => {
    const html = renderToStaticMarkup(
      createElement(QuintaOverview, {
        quinta,
        map: { ...mapData, geometry: null, vidrieras: [] },
        mapFailed: false,
        vidrieras: [],
        vidrierasMessage: null,
        includeInactive: false,
      }),
    );

    expect(html).toContain("todavía no está ubicada");
    expect(html).toContain("Ubicar en el mapa");
    expect(html).not.toContain('role="application"');
    expect(html).toContain("todavía no tiene vidrieras");
  });

  it("keeps vidrieras reachable when the map cannot be loaded", () => {
    const html = renderToStaticMarkup(
      createElement(QuintaOverview, {
        quinta,
        map: null,
        mapFailed: true,
        vidrieras,
        vidrierasMessage: null,
        includeInactive: false,
      }),
    );

    expect(html).toContain("No se pudo cargar el mapa");
    expect(html).toContain(`href="/produccion/vidrieras/${mappedId}"`);
    expect(html).toContain(`href="/produccion/vidrieras/${unmappedId}"`);
    expect(html).not.toContain('role="application"');
  });
});
