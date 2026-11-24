export type CultivationCycle = {
  id: string;
  vidriera_id: string;
  start_date: string;
  end_date: string | null;
  status: "active" | "finalized";
  notes: string | null;
};

export type CycleCollection = {
  active: CultivationCycle | null;
  history: CultivationCycle[];
};

const CALENDAR_DATE = /^(\d{4})-(\d{2})-(\d{2})$/;

export function isCalendarDate(value: string): boolean {
  const match = CALENDAR_DATE.exec(value);
  if (!match) {
    return false;
  }
  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  const parsed = new Date(Date.UTC(year, month - 1, day));
  return (
    parsed.getUTCFullYear() === year &&
    parsed.getUTCMonth() === month - 1 &&
    parsed.getUTCDate() === day
  );
}

export function formatCycleDate(iso: string): string {
  if (!isCalendarDate(iso)) {
    return iso;
  }
  const [year, month, day] = iso.split("-");
  return `${day}/${month}/${year}`;
}

export function cycleStatusLabel(status: CultivationCycle["status"]): string {
  return status === "active" ? "Activo" : "Finalizado";
}

export function plantingDateError(value: string): string | null {
  if (!isCalendarDate(value)) {
    return "La fecha de plantación debe ser una fecha válida (AAAA-MM-DD).";
  }
  return null;
}

export function closingDateError(
  start: string,
  end: string,
  confirmed: boolean,
): string | null {
  if (!isCalendarDate(end)) {
    return "La fecha de cierre debe ser una fecha válida (AAAA-MM-DD).";
  }
  if (end < start) {
    return "La fecha de cierre no puede ser anterior a la plantación.";
  }
  if (!confirmed) {
    return "Confirme el cierre del ciclo.";
  }
  return null;
}

export function suggestedClosingDate(now: Date = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Argentina/Buenos_Aires",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(now);
}
