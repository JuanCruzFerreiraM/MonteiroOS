import { describe, expect, it } from "vitest";

import { currentNavigationItem, isCurrentItem, navigation } from "./navigation";

describe("navigation", () => {
  it("enables only Inicio", () => {
    const available = navigation.filter((item) => item.available);

    expect(available.map((item) => item.label)).toEqual(["Inicio"]);
    expect(available[0]?.href).toBe("/");
  });

  it("keeps future modules visible and without a destination", () => {
    const unavailable = navigation.filter((item) => !item.available);

    expect(unavailable.map((item) => item.label)).toEqual([
      "Producción",
      "Operaciones",
      "Cosechas",
      "Inventario",
      "Comercialización",
      "Configuración",
    ]);
    expect(unavailable.every((item) => !("href" in item))).toBe(true);
  });

  it("matches the home route exactly", () => {
    const home = navigation[0];

    expect(isCurrentItem(home, "/")).toBe(true);
    expect(isCurrentItem(home, "/produccion")).toBe(false);
    expect(currentNavigationItem("/")?.id).toBe("inicio");
    expect(currentNavigationItem("/produccion")).toBeUndefined();
  });
});
