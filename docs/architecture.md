# Arquitectura

Monteiro OS es un monolito modular. Un solo backend y un solo frontend se despliegan y se desarrollan juntos. Los límites entre áreas de negocio son módulos de código, no servicios de red.

## Arquitectura actual

```text
navegador → frontend (Next.js) → todavía sin llamadas de negocio
                backend (FastAPI) → PostgreSQL
```

- **Frontend.** Aplicación Next.js. Hoy solo demuestra que el cascarón funciona. No hay navegación ni pantallas de negocio.
- **Backend.** Un proceso FastAPI. Expone una API REST. El único endpoint actual es `GET /health`.
- **Persistencia.** PostgreSQL. SQLAlchemy 2 abre la conexión y Alembic es el mecanismo de migraciones. `Base` existe para los modelos futuros. No hay tablas de dominio.
- **Configuración.** Variables de entorno, con valores por defecto para desarrollo local. Ver `.env.example`.
- **Límite de la API.** El frontend y cualquier otro cliente hablan con el backend por HTTP/JSON. No hay otra frontera de integración activa.

Principios que ya aplican:

- un repositorio y un proceso de backend;
- tecnología estable y común;
- no agregar infraestructura sin un uso presente;
- la configuración y el esquema se versionan con el código;
- los checks automáticos cubren lint, formato, tests y build.

Estructura del backend hoy:

```text
backend/
├── app/
│   ├── main.py           construcción de la aplicación
│   ├── api/              rutas HTTP
│   └── core/             configuración y base de datos
├── alembic/              migraciones
└── tests/
```

## Capacidades futuras posibles

Cuando el dominio esté entendido, las áreas pueden aparecer como módulos dentro del mismo proceso, por ejemplo `backend/app/modules/production`, `commercial`, `finance` y `analytics`. Cada módulo tendría sus modelos, rutas y casos de uso. Seguirían compartiendo una base PostgreSQL, una configuración y un despliegue.

Eso no está creado. No hay esqueletos vacíos de esos módulos.

Más adelante, y solo con una necesidad concreta, podrían sumarse entrada por voz, ingesta de sensores, modelos predictivos u otros clientes de la misma API. Esas piezas no forman parte de la arquitectura actual y no hay colas, cachés ni servicios separados reservados para ellas.
