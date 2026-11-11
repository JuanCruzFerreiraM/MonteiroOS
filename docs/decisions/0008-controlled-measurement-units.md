# ADR 0008 — Use a controlled unit catalog

- Status: Accepted
- Date: 2026-10-28

## Decision

Every stored quantity references a unit in the measurement catalog. Units belong to a dimension. Conversions are allowed only when they are dimensionally valid. Count units for plants, vara (stem), and ramo (bunch) do not convert among themselves. The unit catalog stores no stems-per-bunch factor.

A commercial presentation may declare an explicit number of varas per ramo for that presentation only. That number is not a unit conversion. Totals use it only when the measurement cites that presentation, and they label the result as derived from the presentation.

## Consequences

- CORE-02 exists before features that persist a quantity, except the first operation slice, which may be notes-only until units exist.
- Forms offer units of the relevant dimension instead of a free-text field.
- A referenced unit is deactivated rather than deleted.
