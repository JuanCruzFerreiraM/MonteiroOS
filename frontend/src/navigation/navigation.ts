export type NavigationItem = {
  id: string;
  label: string;
  href?: string;
  available: boolean;
};

export const navigation = [
  { id: "inicio", label: "Inicio", href: "/", available: true },
  { id: "produccion", label: "Producción", available: false },
  { id: "operaciones", label: "Operaciones", available: false },
  { id: "cosechas", label: "Cosechas", available: false },
  { id: "inventario", label: "Inventario", available: false },
  { id: "comercializacion", label: "Comercialización", available: false },
  { id: "configuracion", label: "Configuración", available: false },
] as const satisfies readonly NavigationItem[];

export function isCurrentItem(item: NavigationItem, pathname: string): boolean {
  if (!item.available || item.href === undefined) {
    return false;
  }
  if (item.href === "/") {
    return pathname === "/";
  }
  return pathname === item.href || pathname.startsWith(`${item.href}/`);
}

export function currentNavigationItem(
  pathname: string,
): NavigationItem | undefined {
  return navigation.find((item) => isCurrentItem(item, pathname));
}
