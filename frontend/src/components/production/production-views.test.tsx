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
  CanteroList,
  EmptyState,
  FormError,
  QuintaList,
  VidrieraList,
} from "./production-views";

const quintas = [
  {
    id: "q1",
    code: "VE",
    name: "Villa Elisa",
    notes: null,
    active: true,
  },
  {
    id: "q2",
    code: "AS",
    name: "Arturo Seguí",
    notes: null,
    active: false,
  },
];

describe("production views", () => {
  it("renders an empty quinta list without sample records", () => {
    const html = renderToStaticMarkup(
      createElement(QuintaList, { quintas: [] }),
    );

    expect(html).toContain("Todavía no hay quintas");
    expect(html).not.toContain("Villa Elisa");
  });

  it("links each quinta and shows its code and state", () => {
    const html = renderToStaticMarkup(createElement(QuintaList, { quintas }));

    expect(html).toContain('href="/produccion/quintas/q1"');
    expect(html).toContain("VE");
    expect(html).toContain("Activa");
    expect(html).toContain("Inactiva");
  });

  it("explains an empty vidriera list and links to creation", () => {
    const html = renderToStaticMarkup(
      createElement(VidrieraList, {
        quintaId: "q1",
        vidrieras: [],
        allowCreate: true,
      }),
    );

    expect(html).toContain("todavía no tiene vidrieras");
    expect(html).toContain('href="/produccion/quintas/q1/vidrieras/nueva"');
  });

  it("shows four canteros in numeric order with their labels", () => {
    const html = renderToStaticMarkup(
      createElement(CanteroList, {
        vidrieraId: "v1",
        canteros: [
          {
            id: "c4",
            number: 4,
            display_code: "VE-V001-C4",
            name: null,
            active: true,
          },
          {
            id: "c1",
            number: 1,
            display_code: "VE-V001-C1",
            name: "Norte",
            active: true,
          },
          {
            id: "c2",
            number: 2,
            display_code: "VE-V001-C2",
            name: null,
            active: false,
          },
          {
            id: "c3",
            number: 3,
            display_code: "VE-V001-C3",
            name: null,
            active: true,
          },
        ],
      }),
    );

    expect(html.indexOf(">C1<")).toBeLessThan(html.indexOf(">C2<"));
    expect(html.indexOf(">C2<")).toBeLessThan(html.indexOf(">C3<"));
    expect(html.indexOf(">C3<")).toBeLessThan(html.indexOf(">C4<"));
    expect(html).toContain("VE-V001-C1");
    expect(html).toContain('href="/produccion/canteros/c1/editar?vidriera=v1"');
    expect(html).toContain("Inactiva");
  });

  it("shows validation feedback", () => {
    const html = renderToStaticMarkup(
      createElement(FormError, { message: "El código ya existe." }),
    );
    const empty = renderToStaticMarkup(
      createElement(EmptyState, {
        title: "Sin registros",
        body: "Cree el primero.",
      }),
    );

    expect(html).toContain('role="alert"');
    expect(html).toContain("El código ya existe.");
    expect(empty).toContain("Sin registros");
  });
});
