import { describe, expect, it, vi } from "vitest";

import type { QuintaMap } from "./production";
import {
  dispatchPolygonClick,
  polygonsForOverview,
  polygonClickEffect,
} from "./map-interaction";

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

const mapData: QuintaMap = {
  id: "q1",
  code: "VE",
  name: "Villa Elisa",
  active: true,
  geometry: square,
  vidrieras: [
    {
      id: "11111111-1111-4111-8111-111111111111",
      code: "VE-V001",
      name: "Norte",
      active: true,
      geometry: square,
      warnings: [],
    },
    {
      id: "22222222-2222-4222-8222-222222222222",
      code: "VE-V002",
      name: "Sur",
      active: true,
      geometry: null,
      warnings: [],
    },
  ],
};

describe("map interaction", () => {
  it("navigates from a vidriera polygon only in the read-only map", () => {
    const view = polygonClickEffect("view", {
      kind: "vidriera",
      id: "11111111-1111-4111-8111-111111111111",
    });
    const edit = polygonClickEffect("edit", {
      kind: "vidriera",
      id: "11111111-1111-4111-8111-111111111111",
    });

    expect(view).toEqual({
      type: "navigate",
      href: "/produccion/vidrieras/11111111-1111-4111-8111-111111111111",
    });
    expect(edit).toEqual({
      type: "select",
      id: "11111111-1111-4111-8111-111111111111",
    });
  });

  it("does not navigate when the quinta boundary is clicked", () => {
    expect(polygonClickEffect("view", { kind: "quinta" })).toEqual({
      type: "none",
    });
    expect(polygonClickEffect("edit", { kind: "quinta" })).toEqual({
      type: "none",
    });
  });

  it("keeps editor clicks on selection and sends viewer clicks to the vidriera", () => {
    const navigate = vi.fn();
    const select = vi.fn();
    const target = {
      kind: "vidriera" as const,
      id: "11111111-1111-4111-8111-111111111111",
    };

    dispatchPolygonClick("view", target, { navigate, select });
    dispatchPolygonClick("edit", target, { navigate, select });
    dispatchPolygonClick("view", { kind: "quinta" }, { navigate, select });

    expect(navigate).toHaveBeenCalledTimes(1);
    expect(navigate).toHaveBeenCalledWith(
      "/produccion/vidrieras/11111111-1111-4111-8111-111111111111",
    );
    expect(select).toHaveBeenCalledTimes(1);
    expect(select).toHaveBeenCalledWith("11111111-1111-4111-8111-111111111111");
  });

  it("renders saved vidriera polygons and skips vidrieras without geometry", () => {
    const polygons = polygonsForOverview(mapData);

    expect(polygons.map((polygon) => polygon.kind)).toEqual([
      "quinta",
      "vidriera",
    ]);
    expect(polygons[1]).toMatchObject({
      id: "11111111-1111-4111-8111-111111111111",
      code: "VE-V001",
    });
    expect(JSON.stringify(polygons)).not.toContain(
      "22222222-2222-4222-8222-222222222222",
    );
  });
});
