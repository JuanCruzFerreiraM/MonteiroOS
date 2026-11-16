export type Quinta = {
  id: string;
  code: string;
  name: string;
  notes: string | null;
  active: boolean;
};

export type Vidriera = {
  id: string;
  quinta_id: string;
  code: string;
  name: string;
  notes: string | null;
  active: boolean;
};

export type Cantero = {
  id: string;
  number: number;
  display_code: string;
  name: string | null;
  active: boolean;
};

export type VidrieraDetail = Vidriera & {
  quinta_code: string;
  quinta_name: string;
  canteros: Cantero[];
};

export type NextVidrieraCode = {
  code: string;
  number: number;
};

export type FormState = {
  error?: string;
};

export function activeLabel(active: boolean): string {
  return active ? "Activa" : "Inactiva";
}
