import { createElement, type ReactNode } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
}));

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

import { AppShell } from "./app-shell";

describe("AppShell", () => {
  it("renders the desktop shell without presenting future modules as ready", () => {
    const html = renderToStaticMarkup(
      createElement(
        AppShell,
        null,
        createElement("p", null, "Contenido principal"),
      ),
    );

    expect(html).toContain("<nav");
    expect(html).toContain("<main");
    expect(html).toContain("Contenido principal");
    expect(html).toContain("Inicio");
    expect(html).toContain('aria-current="page"');
    expect(html).toContain("Producción");
    expect(html).toContain('href="/produccion"');
    expect(html).toContain("Operaciones");
    expect(html).toContain("Aún no disponible");
    expect(html).not.toContain('href="/operaciones"');
    expect(html).not.toContain("quintas registradas");
    expect(html).toContain("min-w-[1280px]");
  });
});
