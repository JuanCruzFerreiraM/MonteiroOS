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

import { ScheduleList, ScheduleSection } from "./schedule-panel";
import type { Occurrence, ScheduleSeries } from "@/lib/schedules";

const pending: Occurrence = {
  series_id: "series-1",
  revision_id: "rev-1",
  vidriera_id: "vid-1",
  occurrence_date: "2024-06-01",
  operation_type: "black_nylon",
  operation_label: "Cobertura con nylon negro",
  status: "unverified",
  expected_start: "2024-06-01T21:00:00Z",
  expected_end: "2024-06-02T11:00:00Z",
  actual_start: null,
  actual_end: null,
  timing_basis: null,
  confirmation_method: null,
  suggested_cycle_id: null,
  cycle_id: null,
  operation_id: null,
  notes: null,
};

const series: ScheduleSeries = {
  series_id: "series-1",
  current: {
    id: "rev-1",
    series_id: "series-1",
    vidriera_id: "vid-1",
    operation_type: "artificial_lighting",
    operation_label: "Iluminación artificial",
    effective_start: "2024-12-01",
    effective_end: "2024-12-20",
    weekdays: [1, 2, 3, 4, 5, 6, 7],
    start_time: "22:00:00",
    end_time: "02:00:00",
    notes: null,
    status: "active",
    generates: true,
    created_at: "2024-11-01T00:00:00Z",
    updated_at: "2024-11-01T00:00:00Z",
  },
  revisions: [],
};

describe("schedule panel", () => {
  it("shows an empty pending state and the confirmation link", () => {
    const html = renderToStaticMarkup(
      <ScheduleSection vidrieraId="vid-1" pending={[]} />,
    );
    expect(html).toContain("No hay confirmaciones pendientes");
    expect(html).toContain("/produccion/vidrieras/vid-1/confirmaciones");
  });

  it("counts pending occurrences and lists a schedule", () => {
    const pendingHtml = renderToStaticMarkup(
      <ScheduleSection vidrieraId="vid-1" pending={[pending]} />,
    );
    const listHtml = renderToStaticMarkup(
      <ScheduleList schedules={[series]} />,
    );
    expect(pendingHtml).toContain("1 ocurrencia pendiente");
    expect(listHtml).toContain("Iluminación artificial");
    expect(listHtml).toContain("22:00–02:00");
    expect(listHtml).toContain("/produccion/programacion/series-1");
  });

  it("shows a load error", () => {
    const html = renderToStaticMarkup(
      <ScheduleSection
        vidrieraId="vid-1"
        pending={null}
        loadError="No se pudo consultar el servicio."
      />,
    );
    expect(html).toContain("No se pudo consultar el servicio.");
  });
});
