# ADR 0006 — Do not encode medianero financial rules yet

- Status: Accepted
- Date: 2026-10-28

## Decision

Medianero assignments record who was responsible for a vidriera over an interval. They do not record a share of cost, revenue, or product supply. Those rules are unknown.

Cost and sale features leave economic responsibility empty unless a user explicitly sets it on a single record. There is no default percentage split.

## Consequences

- PROD-05 is unblocked.
- COST-02 and COST-03 must not invent a settlement.
- [OQ-13](../OPEN_QUESTIONS.md#oq-13), [OQ-14](../OPEN_QUESTIONS.md#oq-14), and [OQ-17](../OPEN_QUESTIONS.md#oq-17) remain the gate for any automatic sharing.
