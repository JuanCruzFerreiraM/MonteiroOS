import Link from "next/link";

import { QuintaCreateForm } from "@/app/produccion/forms";

export const dynamic = "force-dynamic";

export default function NuevaQuintaPage() {
  return (
    <div className="space-y-6">
      <Link
        href="/produccion"
        className="text-sm font-medium text-accent-strong underline-offset-2 hover:underline"
      >
        Volver a producción
      </Link>
      <h2 className="text-2xl font-semibold">Nueva quinta</h2>
      <QuintaCreateForm />
    </div>
  );
}
