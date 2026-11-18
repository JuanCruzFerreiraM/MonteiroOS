import { navigation } from "@/navigation/navigation";
import { readSystemStatus, type SystemStatus } from "@/lib/system-status";

export const dynamic = "force-dynamic";

const statusCopy: Record<SystemStatus["state"], string> = {
  ok: "La base de datos responde.",
  database_unavailable:
    "La base de datos no responde. No se muestra un historial vacío como si hubiera producción registrada.",
  backend_unavailable:
    "No se pudo consultar el servicio. Esa falla no se presenta como una producción vacía.",
  access_denied:
    "El servicio rechazó el acceso. Revise la configuración de protección del despliegue. No hay datos de producción para mostrar.",
};

export default async function Home() {
  const status = await readSystemStatus();
  const pending = navigation.filter((item) => !item.available);
  const failed = status.state !== "ok";

  return (
    <div className="max-w-3xl space-y-8">
      <section className="space-y-3">
        <h2 className="text-2xl font-semibold tracking-tight">Monteiro OS</h2>
        <p className="text-base leading-7 text-ink">
          Registro interno de la producción de Monteiro. La aplicación guarda lo
          que ocurre en el cultivo para poder reconstruirlo después.
        </p>
        <p className="text-base leading-7 text-muted">
          Los módulos se incorporan de a uno. Producción ya permite registrar
          quintas, vidrieras y canteros.
        </p>
      </section>

      <section
        aria-labelledby="system-status-title"
        className={`rounded-lg border bg-surface px-5 py-4 ${
          failed ? "border-warning" : "border-line"
        }`}
      >
        <h2 id="system-status-title" className="text-sm font-semibold">
          Estado actual
        </h2>
        <p className="mt-2 text-sm leading-6" role="status">
          {statusCopy[status.state]}
        </p>
      </section>

      <section aria-labelledby="modules-title" className="space-y-3">
        <h2 id="modules-title" className="text-sm font-semibold">
          Módulos previstos
        </h2>
        <ul className="divide-y divide-line rounded-lg border border-line bg-surface">
          {pending.map((item) => (
            <li
              key={item.id}
              className="flex items-center justify-between px-5 py-3 text-sm"
            >
              <span>{item.label}</span>
              <span className="text-muted">Aún no disponible</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
