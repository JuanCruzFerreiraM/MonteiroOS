# ADR 0005 — Keep the product catalog separate from stock

- Status: Accepted
- Date: 2026-10-28

## Decision

A product is a catalog identity. Stock is a quantity of that product at a location, introduced only in Stage 3. An application stores the product and the quantity used. That quantity is not a stock movement.

Purchases, storage locations, and movements are their own records and may later cite an application or a purchase. They are not columns on the product.

## Consequences

- INV-01 can ship in Stage 1 with no balance.
- OPS-02 can record applications before any warehouse exists.
- INV-03 must not backfill balances from historical applications unless a user explicitly records a movement.
