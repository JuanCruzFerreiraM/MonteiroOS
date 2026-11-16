# CORE-01 — Application Foundation

## Metadata
- ID: CORE-01
- Module: Access
- Stage: 1
- Status: In Progress
- Priority: P0
- Domains: `FRONTEND` `BACKEND` `DATABASE` `INFRA`
- Dependencies: None

## Objective

Provide a single-user, desktop-first application shell on the existing FastAPI, Next.js, and PostgreSQL foundation, with persistent data and a recoverable database.

## Business Value

The business needs one reliable place to record production. The first release is for internal use by one operator at a desk. Account directories and phone workflows would add complexity before any production history exists.

## Functional Description

The repository already runs a Next.js placeholder, a FastAPI process with `GET /health`, PostgreSQL, Alembic with no revisions, Docker Compose, and CI. This feature completes that foundation. It does not replace the stack and does not add a native desktop application.

The MVP has one software user: whoever can open the deployed application. It does not register people, roles, or concurrent sessions. Business people are recorded later in CORE-03 and are not accounts.

Access protection is deployment-appropriate and basic. A single shared secret, or an equivalent network restriction documented for the chosen deployment, may guard the application. It does not identify a person and it does not authorize individual actions. `GET /health` stays available without that secret so process checks keep working.

The shell is a desktop layout: a stable navigation region and a content area sized for a wide window. Later features add destinations. There is no separate mobile navigation.

PostgreSQL remains the store. The feature documents a backup and restore path using the existing database volume and `pg_dump` / `pg_restore`. That path is part of the foundation, not a second product.

The application is the intended long-term source of truth for production information. This feature only makes the shell and the database ready to hold it.

## Expected Behavior

- `GET /health` returns `{"status": "ok"}` when PostgreSQL accepts `SELECT 1`, and `503` when it does not.
- Opening the application on a desktop window shows the shell.
- Production screens, once they exist, are reachable from that shell without a second account.
- If the deployment secret is configured, requests without it do not receive production data. Health still responds.
- A documented backup can be restored into an empty database of the same major version.

## Business Rules

- The MVP supports one software user. See [ADR 0009](../decisions/0009-single-user-desktop-first.md).
- Business participants do not need software accounts.
- Desktop-first means the layout and acceptance target a desktop window. It does not require a native client.
- Multi-user access and mobile-specific UX are future evolution, not this feature.

## Data Requirements

No person or account catalog.

| Fact | Required |
| --- | --- |
| Optional deployment secret, outside the database and outside git | No |
| PostgreSQL database used by the application | Yes |

## User Interactions

- Open the application on a desktop browser and land in the shell.
- Use the navigation region to reach features as they are added.
- Follow the documented backup and restore steps when a copy of the database is required.

## Acceptance Criteria

- [ ] Initial workflows support one software user.
- [ ] Desktop workflows are usable without mobile-specific navigation or layouts.
- [ ] No account directory, role-based access control, or per-person login is required to open the shell.
- [ ] Production data is stored in PostgreSQL and remains after the application process restarts.
- [ ] A backup taken with the documented procedure can be restored and read back.
- [ ] `GET /health` returns ok when the database is reachable and 503 when it is not.
- [ ] Existing backend health tests still pass.
- [ ] The shell shows a navigation region at a desktop width of at least 1280 pixels.

## Edge Cases & Validation

- A missing database fails health and does not present an empty production history as if it were real.
- The deployment secret is not committed and is not displayed in the shell.
- The Spanish document language stays `es`.

## Out of Scope

- Multi-user registration, sessions per person, SSO, password reset, and a permission matrix.
- Employee or medianero portals.
- Mobile-specific UX, offline use, and multi-device sync.
- Concurrent editing and audit trails based on multiple software accounts.
- Domain screens for farms, operations, or catalogs.
- A native desktop shell. The existing web application remains the client.
- A brand system. No logo is present to preserve.

## Dependencies & Integration Points

- Uses the current FastAPI application, Next.js app, PostgreSQL, Alembic, Compose, and CI as they are.
- Later features persist through this database. They do not add accounts in order to name a person.
- [OQ-20](../OPEN_QUESTIONS.md#oq-20) is resolved for the MVP. Multi-user and mobile clients stay on the future list in the [roadmap](../product/ROADMAP.md).

## Open Questions

None for this feature. [OQ-20](../OPEN_QUESTIONS.md#oq-20) records the deferred multi-user and mobile decision.

## Implementation notes

Status stays `In Progress` until this branch is reviewed and the pull request checks are green. The behavior below is what the branch contains.

- The web app replaces the placeholder with a desktop shell: sidebar, heading, and main region. The layout is at least 1280 pixels wide. Copy is Spanish. `lang` remains `es`.
- Navigation is a single list in `frontend/src/navigation/navigation.ts`. Inicio is the only enabled destination. Producción, Operaciones, Cosechas, Inventario, Comercialización, and Configuración are visible and labeled "Aún no disponible". They have no route and no sample business data. A later feature enables an item by setting `available` and `href`.
- The home page reads `GET /health` on the server. A database or backend failure is shown as a failure. It is not presented as an empty production history.
- Local Compose publishes the database, API, and web ports on `127.0.0.1` only. That is the local network restriction.
- `APP_ACCESS_SECRET`, when set to a non-blank value, makes every backend route except `GET /health` require the header `X-Monteiro-Access`. The Next.js server may send that header from its own environment. The value is not a `NEXT_PUBLIC_` variable, not a browser token, and not a user account. When the secret is unset, the API does not add a login; loopback binding is the local boundary. Publishing the API beyond loopback without the secret is not a supported deployment.
- Backup and restore are documented in [BACKUP.md](../development/BACKUP.md). The restore script refuses the primary database.
