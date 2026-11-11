# Definition of done

A feature moves to `Implemented` only when all of the following are true.

## Product

- The acceptance criteria in its specification are satisfied, including the stated failure cases.
- Important edge cases in the specification were tried, not only the happy path.
- No known critical regression remains in flows that share the changed models or screens.
- For a user-facing change, the affected flow was exercised in a browser, including the error shown when validation fails.
- Technical completion is separate from field validation. If the business still needs to confirm a non-blocking question, the pull request says so and the feature does not pretend the question is answered.

## Engineering

- Relevant automated tests pass, including backend tests against PostgreSQL when persistence changed.
- CI jobs `backend` and `frontend` are green when those areas change.
- Database changes ship as an Alembic revision reviewed with the model. The revision is not an empty placeholder.
- Documentation is updated when behavior, setup, status, or an open question changed.
- No secrets, `.env` files, or real personal data are committed.
- The pull request was reviewed.
- The change stays inside the modular monolith and the current stack.

## Status hygiene

- [FEATURES.md](../../FEATURES.md) shows the new status.
- A partial pull request leaves the feature `In Progress`.
- `Deferred` is used only when the work is intentionally postponed, with the reason recorded on the specification.
