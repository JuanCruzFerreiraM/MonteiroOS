import Link from "next/link";

import { isCurrentItem, type NavigationItem } from "@/navigation/navigation";

type SidebarNavProps = {
  items: readonly NavigationItem[];
  currentPath: string;
};

export function SidebarNav({ items, currentPath }: SidebarNavProps) {
  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-line px-5 py-6">
        <p className="text-xs font-medium tracking-wide text-muted uppercase">
          Monteiro
        </p>
        <p className="mt-1 text-lg font-semibold text-ink">Monteiro OS</p>
      </div>
      <nav aria-label="Secciones" className="flex-1 px-3 py-4">
        <ul className="space-y-1">
          {items.map((item) => {
            const current = isCurrentItem(item, currentPath);
            if (item.available && item.href) {
              return (
                <li key={item.id}>
                  <Link
                    href={item.href}
                    aria-current={current ? "page" : undefined}
                    className={`block rounded-md px-3 py-2 text-sm font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent ${
                      current
                        ? "bg-accent/10 text-accent-strong"
                        : "text-ink hover:bg-background"
                    }`}
                  >
                    {item.label}
                  </Link>
                </li>
              );
            }
            return (
              <li key={item.id}>
                <div className="rounded-md px-3 py-2">
                  <p className="text-sm font-medium text-muted">{item.label}</p>
                  <p className="text-xs text-muted">Aún no disponible</p>
                </div>
              </li>
            );
          })}
        </ul>
      </nav>
    </div>
  );
}
