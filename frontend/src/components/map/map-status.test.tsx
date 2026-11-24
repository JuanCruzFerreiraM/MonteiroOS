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

import { missingImageryConfig, readyImageryConfig } from "../../lib/imagery";
import { MapStatus } from "./map-status";

const idle = {
  query: "",
  onQueryChange: () => undefined,
  onSearch: () => undefined,
  searching: false,
  searchError: null,
  results: [],
  onSelectResult: () => undefined,
  tileError: false,
  mapFailed: false,
  geometryError: false,
  hasBoundary: false,
};

describe("map status", () => {
  it("explains a missing imagery key and keeps the production list reachable", () => {
    const html = renderToStaticMarkup(
      createElement(MapStatus, {
        ...idle,
        imagery: missingImageryConfig(),
      }),
    );

    expect(html).toContain("ESRI_API_KEY");
    expect(html).toContain("no se borran");
    expect(html).toContain('href="/produccion"');
    expect(html).toContain("disabled");
    expect(html).toContain("huella aproximada");
    expect(html).toContain("todavía no tiene un límite");
  });

  it("separates a tile failure from an empty boundary", () => {
    const html = renderToStaticMarkup(
      createElement(MapStatus, {
        ...idle,
        hasBoundary: true,
        tileError: true,
        imagery: readyImageryConfig({
          attribution: "Esri, Maxar",
          maxZoom: 19,
          tileSize: 256,
        }),
      }),
    );

    expect(html).toContain("imágenes satelitales");
    expect(html).toContain("no se modificaron");
    expect(html).not.toContain("todavía no tiene un límite");
  });

  it("shows a geometry drawing failure without blaming the imagery", () => {
    const html = renderToStaticMarkup(
      createElement(MapStatus, {
        ...idle,
        hasBoundary: true,
        geometryError: true,
        imagery: readyImageryConfig({
          attribution: "Esri, Maxar",
          maxZoom: 19,
          tileSize: 256,
        }),
      }),
    );

    expect(html).toContain("no se pudo dibujar");
    expect(html).not.toContain("imágenes satelitales");
  });
});
