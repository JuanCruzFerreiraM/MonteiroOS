"use client";

import { usePathname } from "next/navigation";

import { currentNavigationItem } from "@/navigation/navigation";

export function PageHeading() {
  const pathname = usePathname();
  const current = currentNavigationItem(pathname);

  return (
    <div>
      <p className="text-sm text-muted">Monteiro OS</p>
      <h1 className="text-xl font-semibold text-ink">
        {current?.label ?? "Monteiro OS"}
      </h1>
    </div>
  );
}
