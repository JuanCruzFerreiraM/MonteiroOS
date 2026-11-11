# INV-02 — Storage Locations

## Metadata
- ID: INV-02
- Module: Inventory
- Stage: 3
- Status: Planned
- Priority: P2
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: CORE-01

## Objective

Name the places where cultivation products are stored, without recording quantities.

## Business Value

Later stock movements need a location. Inventing a warehouse tree before the business names its places would misstate the operation.

## Functional Description

Users create storage locations with a name, an optional parent location, optional notes, and an active flag. The parent allows a shallow organization if the business uses one. A location is not required to have a parent.

No quantities are stored on the location. No locations are seeded.

## Expected Behavior

- The user can create, rename, and deactivate a location.
- A location can sit under another location.
- A cycle in the parent chain is rejected.
- A deactivated location cannot receive new stock later and remains readable.

## Business Rules

- Locations are user-entered. See [OQ-19](../OPEN_QUESTIONS.md#oq-19).
- A location is not a product and not a vidriera.

## Data Requirements

| Fact | Required |
| --- | --- |
| Name, unique among siblings | Yes |
| Parent location | No |
| Notes | No |
| Active flag | Yes |

## User Interactions

- Add a location from the inventory settings area.
- Nest one location under another.
- Deactivate a location that is no longer used.

## Acceptance Criteria

- [ ] A location can be saved with only a name.
- [ ] A location can be saved with a parent.
- [ ] Setting a location as its own ancestor is rejected.
- [ ] Two locations with the same parent cannot share a name.
- [ ] The same name is accepted under different parents.
- [ ] Deactivating a location hides it from the default list and leaves it readable.
- [ ] The location screen does not show or require a quantity.

## Edge Cases & Validation

- An empty name is rejected.
- A location that later has stock cannot be deleted. This feature rejects deletion whenever the location exists, and deactivation is the supported action, so INV-03 does not need a special case on day one.

## Out of Scope

- Stock balances (INV-03).
- Maps of storage.
- A seeded layout of the farms.

## Dependencies & Integration Points

- CORE-01 for access.
- INV-03 attaches quantities to these locations.

## Open Questions

- [OQ-19](../OPEN_QUESTIONS.md#oq-19) is non-blocking. It blocks only a predefined location tree.
