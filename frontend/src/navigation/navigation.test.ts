import { describe, expect, it } from "vitest";

import { currentNavigationItem, isCurrentItem, navigation } from "./navigation";

describe("navigation", () => {
  it("enables Inicio and Producción", () => {
    const available = navigation.filter((item) => item.available);

    expect(available.map((item) => item.label)).toEqual([
      "Inicio",
      "Producción",
    ]);
    expect(available[0]?.href).toBe("/");
    expect(available[1]?.href).toBe("/produccion");
  });

  it("keeps future modules visible and without a destination", () => {
    const unavailable = navigation.filter((item) => !item.available);

    expect(unavailable.map((item) => item.label)).toEqual([
      "Operaciones",
      "Cosechas",
      "Inventario",
      "Comercialización",
      "Configuración",
    ]);
    expect(unavailable.every((item) => !("href" in item))).toBe(true);
  });

  it("matches the home route exactly and production routes as Producción", () => {
    const home = navigation[0];
    const production = navigation[1];

    expect(isCurrentItem(home, "/")).toBe(true);
    expect(isCurrentItem(home, "/produccion")).toBe(false);
    expect(isCurrentItem(production, "/produccion")).toBe(true);
    expect(isCurrentItem(production, "/produccion/quintas/1")).toBe(true);
    expect(currentNavigationItem("/")?.id).toBe("inicio");
    expect(currentNavigationItem("/produccion/vidrieras/1")?.id).toBe(
      "produccion",
    );
  });
});
