export const WEEKDAYS = [
  { value: 1, label: "Lunes" },
  { value: 2, label: "Martes" },
  { value: 3, label: "Miércoles" },
  { value: 4, label: "Jueves" },
  { value: 5, label: "Viernes" },
  { value: 6, label: "Sábado" },
  { value: 7, label: "Domingo" },
] as const;

export type ScheduleStatus = "active" | "paused" | "ended";
export type OccurrenceStatus =
  "scheduled" | "unverified" | "confirmed" | "not_occurred";

export type ScheduleRevision = {
  id: string;
  series_id: string;
  vidriera_id: string;
  operation_type: "artificial_lighting" | "black_nylon";
  operation_label: string;
  effective_start: string;
  effective_end: string;
  weekdays: number[];
  start_time: string;
  end_time: string;
  notes: string | null;
  status: ScheduleStatus;
  generates: boolean;
  created_at: string;
  updated_at: string;
};

export type ScheduleSeries = {
  series_id: string;
  current: ScheduleRevision;
  revisions: ScheduleRevision[];
};

export type Occurrence = {
  series_id: string;
  revision_id: string;
  vidriera_id: string;
  occurrence_date: string;
  operation_type: string;
  operation_label: string;
  status: OccurrenceStatus;
  expected_start: string;
  expected_end: string;
  actual_start: string | null;
  actual_end: string | null;
  timing_basis: "operator_entered" | "assumed_from_schedule" | null;
  confirmation_method: "manual" | null;
  suggested_cycle_id: string | null;
  cycle_id: string | null;
  operation_id: string | null;
  notes: string | null;
};

const CLOCK = /^([01]\d|2[0-3]):[0-5]\d$/;

export function civilToday(now = new Date()): string {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Argentina/Buenos_Aires",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(now);
  const value = (type: string) =>
    parts.find((part) => part.type === type)?.value;
  return `${value("year")}-${value("month")}-${value("day")}`;
}

export function addDays(iso: string, days: number): string {
  const [year, month, day] = iso.split("-").map(Number);
  const shifted = new Date(Date.UTC(year, month - 1, day + days));
  return shifted.toISOString().slice(0, 10);
}

export function clockInput(value: string): string {
  return value.slice(0, 5);
}

export function weekdayLabels(days: number[]): string {
  return WEEKDAYS.filter((day) => days.includes(day.value))
    .map((day) => day.label)
    .join(", ");
}

export function scheduleStatusLabel(status: ScheduleStatus): string {
  if (status === "paused") {
    return "En pausa";
  }
  if (status === "ended") {
    return "Finalizada";
  }
  return "Activa";
}

export function occurrenceStatusLabel(status: OccurrenceStatus): string {
  if (status === "unverified") {
    return "Pendiente de verificación";
  }
  if (status === "confirmed") {
    return "Confirmada";
  }
  if (status === "not_occurred") {
    return "No realizada";
  }
  return "Programada";
}

export function scheduleError(input: {
  start: string;
  end: string;
  weekdays: number[];
  startTime: string;
  endTime: string;
}): string | null {
  if (
    !/^\d{4}-\d{2}-\d{2}$/.test(input.start) ||
    !/^\d{4}-\d{2}-\d{2}$/.test(input.end)
  ) {
    return "Indique el período con fechas válidas.";
  }
  if (input.end < input.start) {
    return "La fecha de fin no puede ser anterior al inicio.";
  }
  if (input.weekdays.length === 0) {
    return "Seleccione al menos un día de la semana.";
  }
  if (!CLOCK.test(input.startTime) || !CLOCK.test(input.endTime)) {
    return "Indique un horario válido.";
  }
  if (input.startTime === input.endTime) {
    return "El inicio y el fin programados no pueden ser iguales.";
  }
  return null;
}
