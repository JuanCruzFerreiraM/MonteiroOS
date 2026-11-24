export const OPERATION_TYPES = [
  "irrigation",
  "artificial_lighting",
  "black_nylon",
  "cold_protection_heating",
  "product_application",
  "manual_labor",
  "observation",
] as const;

export type OperationType = (typeof OPERATION_TYPES)[number];

export type Operation = {
  id: string;
  vidriera_id: string;
  operation_type: OperationType;
  operation_label: string;
  occurred_at: string;
  cycle_id: string | null;
  notes: string | null;
  recorded_at: string;
  updated_at: string;
  origin: "manual" | "scheduled";
  interval_start: string | null;
  interval_end: string | null;
  timing_basis: "operator_entered" | "assumed_from_schedule" | null;
};

const LABELS: Record<OperationType, string> = {
  irrigation: "Riego",
  artificial_lighting: "Iluminación artificial",
  black_nylon: "Cobertura con nylon negro",
  cold_protection_heating: "Calefacción contra el frío",
  product_application: "Aplicación de productos",
  manual_labor: "Mano de obra",
  observation: "Observación",
};

const LOCAL_MOMENT = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})$/;

export function operationLabel(type: string): string {
  if (type in LABELS) {
    return LABELS[type as OperationType];
  }
  return type;
}

export function acceptsInterval(type: string): boolean {
  return type === "artificial_lighting" || type === "black_nylon";
}

export function formatOccurredAt(iso: string): string {
  const parsed = new Date(iso);
  if (Number.isNaN(parsed.getTime())) {
    return iso;
  }
  return new Intl.DateTimeFormat("es-AR", {
    timeZone: "America/Argentina/Buenos_Aires",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).format(parsed);
}

export function toLocalInput(iso: string | null): string {
  if (!iso) {
    return "";
  }
  const parsed = new Date(iso);
  if (Number.isNaN(parsed.getTime())) {
    return "";
  }
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Argentina/Buenos_Aires",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).formatToParts(parsed);
  const value = (type: string) =>
    parts.find((part) => part.type === type)?.value;
  return `${value("year")}-${value("month")}-${value("day")}T${value("hour")}:${value("minute")}`;
}

export function fromLocalInput(value: string): string | null {
  if (!LOCAL_MOMENT.test(value)) {
    return null;
  }
  return `${value}:00-03:00`;
}

export function occurredAtError(value: string): string | null {
  if (!fromLocalInput(value)) {
    return "La fecha y hora deben ser válidas.";
  }
  return null;
}

export function intervalError(start: string, end: string): string | null {
  if (!start && !end) {
    return null;
  }
  if (!start || !end) {
    return "El intervalo real necesita inicio y fin.";
  }
  const startIso = fromLocalInput(start);
  const endIso = fromLocalInput(end);
  if (!startIso || !endIso) {
    return "El intervalo real debe ser una fecha y hora válida.";
  }
  if (Date.parse(endIso) <= Date.parse(startIso)) {
    return "El fin real tiene que ser posterior al inicio.";
  }
  return null;
}

export function timingBasisLabel(
  basis: Operation["timing_basis"],
): string | null {
  if (basis === "assumed_from_schedule") {
    return "Horario supuesto a partir de la programación. No es una medición.";
  }
  if (basis === "operator_entered") {
    return "Horario indicado por el operador.";
  }
  return null;
}
