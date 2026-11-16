import type { ReactNode } from "react";

import { PageHeading } from "./page-heading";
import { Sidebar } from "./sidebar";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen min-w-[1280px] bg-background text-ink">
      <aside className="w-64 shrink-0 border-r border-line bg-surface">
        <Sidebar />
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="border-b border-line bg-surface px-8 py-5">
          <PageHeading />
        </header>
        <main className="flex-1 px-8 py-8">{children}</main>
      </div>
    </div>
  );
}
