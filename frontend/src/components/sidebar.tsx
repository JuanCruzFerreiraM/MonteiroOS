"use client";

import { usePathname } from "next/navigation";

import { navigation } from "@/navigation/navigation";

import { SidebarNav } from "./sidebar-nav";

export function Sidebar() {
  const pathname = usePathname();
  return <SidebarNav items={navigation} currentPath={pathname} />;
}
