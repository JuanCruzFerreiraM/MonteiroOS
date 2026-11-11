# ADR 0004 — Separate operation scope from yield units

- Status: Accepted
- Date: 2026-10-28

## Decision

An operation has a scope of one or more vidrieras and is stored once. Yield and harvest stay on canteros. The system does not duplicate an operation onto each cantero so that reports can sum bed-level rows.

When an operation targets several vidrieras, each target may point at that vidriera's own cultivation cycle, or at none. The operation does not carry a single cycle foreign key.

## Consequences

- OPS-01 ships with a scope of one vidriera.
- OPS-03 extends scope without changing the identity of existing operations.
- TRACE-01 lists the same operation on every targeted vidriera.
- Harvest features do not require operations to be bed-scoped.
