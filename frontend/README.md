# Frontend

Next.js application for Monteiro OS. Setup, commands, and the product documentation are in the [repository README](../README.md).

The package renders the desktop application shell and the Production screens for quintas, vidrieras, and canteros. Other modules stay listed in the sidebar as unavailable. The Production API must already have its schema (`alembic upgrade head` from `backend/`) or those screens report that the schema is missing.

`npm test` runs the Vitest checks for the shell, navigation, and production views. `BACKEND_URL` is the server-side address of the API. `APP_ACCESS_SECRET` is optional, is read only on the server, and must not use a `NEXT_PUBLIC_` name. That secret does not protect this web app if it is published beyond loopback.
