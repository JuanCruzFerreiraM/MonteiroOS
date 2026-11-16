# Frontend

Next.js application for Monteiro OS. Setup, commands, and the product documentation are in the [repository README](../README.md).

The package renders the desktop application shell. Domain screens are specified in [FEATURES.md](../FEATURES.md) and are not implemented in this package yet. Navigation for those screens is listed in the sidebar as unavailable.

`npm test` runs the Vitest checks for the shell and navigation. `BACKEND_URL` is the server-side address of the API. `APP_ACCESS_SECRET` is optional and must not use a `NEXT_PUBLIC_` name.
