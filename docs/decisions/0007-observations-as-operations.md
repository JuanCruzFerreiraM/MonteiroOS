# ADR 0007 — Record observations as operations

- Status: Accepted
- Date: 2026-10-28

## Decision

An observation is an operation type. It appears in the same vidriera history as irrigations and applications. Its structured data describes conditions. It does not imply that a person intervened.

Photographs and other files are attachments linked to an operation. TRACE-02 adds the files. It does not create a second observation log.

## Consequences

- OPS-02 defines the observation payload.
- TRACE-01 shows observations without a special store.
- A lighting or heating note about conditions can be an observation, distinct from an activation record.
