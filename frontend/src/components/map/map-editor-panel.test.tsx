import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { QuintaMap } from "../../lib/production";
import { MapEditorPanel } from "./map-editor-panel";

const mapData: QuintaMap = {
  id: "q1",
  code: "VE",
  name: "Villa Elisa",
  active: true,
  geometry: null,
  vidrieras: [
    {
      id: "v1",
      code: "VE-V001",
      name: "Norte",
      active: true,
      geometry: null,
      warnings: [],
    },
  ],
};

const callbacks = {
  onDrawQuinta: () => undefined,
  onEditQuinta: () => undefined,
  onRedrawQuinta: () => undefined,
  onAskRemove: () => undefined,
  onConfirmRemove: () => undefined,
  onCancelRemove: () => undefined,
  onDrawVidriera: () => undefined,
  onEditVidriera: () => undefined,
  onRemoveVidriera: () => undefined,
  onNewVidriera: () => undefined,
  onDraftCode: () => undefined,
  onDraftName: () => undefined,
  onBeginDraw: () => undefined,
  onSave: () => undefined,
  onCancel: () => undefined,
};

describe("map editor panel", () => {
  it("asks for the quinta boundary before a vidriera polygon", () => {
    const html = renderToStaticMarkup(
      createElement(MapEditorPanel, {
        ...callbacks,
        mapData,
        justCreated: true,
        draft: null,
        saving: false,
        error: null,
        notices: [],
        confirmingRemoval: null,
      }),
    );

    expect(html).toContain("La quinta ya está guardada");
    expect(html).toContain("Dibujar límite de la quinta");
    expect(html).toContain("Dibuje primero el límite de la quinta");
    expect(html).toContain("VE-V001");
    expect(html).toContain("Sin límite");
    expect(html).toContain("disabled");
  });

  it("shows a removal confirmation and keeps warnings distinct from errors", () => {
    const html = renderToStaticMarkup(
      createElement(MapEditorPanel, {
        ...callbacks,
        mapData: {
          ...mapData,
          geometry: {
            type: "Polygon",
            coordinates: [
              [
                [0, 0],
                [1, 0],
                [1, 1],
                [0, 0],
              ],
            ],
          },
          vidrieras: [
            {
              ...mapData.vidrieras[0],
              geometry: {
                type: "Polygon",
                coordinates: [
                  [
                    [0, 0],
                    [0.4, 0],
                    [0.4, 0.4],
                    [0, 0],
                  ],
                ],
              },
              warnings: [
                {
                  code: "vidriera_overlap",
                  message: "El polígono se superpone con VE-V002.",
                  vidriera_id: "v2",
                  vidriera_code: "VE-V002",
                },
              ],
            },
          ],
        },
        justCreated: false,
        draft: null,
        saving: false,
        error: "El polígono se cruza a sí mismo.",
        notices: [
          {
            code: "boundary_overflow",
            message: "El polígono se extiende un poco fuera de la quinta.",
            vidriera_id: null,
            vidriera_code: null,
          },
        ],
        confirmingRemoval: "quinta",
      }),
    );

    expect(html).toContain("La quinta sigue existiendo");
    expect(html).toContain('role="alert"');
    expect(html).toContain("se cruza a sí mismo");
    expect(html).toContain('role="status"');
    expect(html).toContain("Aviso: El polígono se extiende un poco");
    expect(html).toContain("Aviso: El polígono se superpone");
  });
});
