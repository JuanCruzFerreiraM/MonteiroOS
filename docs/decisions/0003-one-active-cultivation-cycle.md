# ADR 0003 — One active cultivation cycle per vidriera

- Status: Accepted
- Date: 2026-10-28

## Decision

A vidriera has at most one active top-level cultivation cycle. Finalized cycles remain stored and queryable. A new cycle can start only after the previous one is finalized. Cycle periods for the same vidriera do not overlap.

Preparation work between cycles is stored without a cycle, or is explicitly detached from the active cycle. It is not attached to a neighboring cycle to fill a required field.

## Consequences

- PROD-03 enforces the rule in the write path, not only in the form.
- Operations and harvests that cite a cycle must cite a cycle of the same vidriera.
- Historical reports read finalized cycles with the same queries as the active one.
