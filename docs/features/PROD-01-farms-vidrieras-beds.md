# PROD-01 — Farms, Vidrieras & Beds

## Metadata
- ID: PROD-01
- Module: Production
- Stage: 1
- Status: Planned
- Priority: P0
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: CORE-01

## Objective

Represent the physical production hierarchy: quinta, vidriera, and cantero.

## Business Value

Every operation and harvest needs a stable place. The vidriera is the place operators manage day to day.

## Functional Description

Authorized users create quintas and, within each, vidrieras. Creating a vidriera also creates four canteros with distinct labels. Users can rename labels. The vidriera detail view shows the quinta, the four canteros, and an empty region where the active cycle and recent activity will appear in later features.

Villa Elisa and Arturo Seguí are not seeded as a hidden fixture. The business creates the properties it uses. Tests may create their own names.

Optional measured area may be stored on a vidriera or a cantero. Empty area means unknown, not zero.

## Expected Behavior

- The user can list quintas, open one, and see its vidrieras.
- The user can open a vidriera and see its canteros.
- Two vidrieras in the same quinta cannot share a name.
- Two canteros in the same vidriera cannot share a label.
- Deactivating a vidriera hides it from new selections and keeps it readable.
- A vidriera or cantero that later has history cannot be deleted.

## Business Rules

- The physical hierarchy is quinta, then vidriera, then cantero. See [PRODUCTION_MODEL.md](../domain/PRODUCTION_MODEL.md).
- Each vidriera has four canteros. See [PRODUCTION_MODEL.md](../domain/PRODUCTION_MODEL.md).
- Area is optional and is never inferred.

## Data Requirements

| Fact | Required |
| --- | --- |
| Quinta name | Yes |
| Quinta notes | No |
| Quinta active flag | Yes |
| Vidriera name, unique within the quinta | Yes |
| Vidriera notes | No |
| Vidriera active flag | Yes |
| Vidriera area and area unit | No |
| Cantero label, unique within the vidriera | Yes |
| Cantero active flag | Yes |
| Cantero area and area unit | No |

Area, when present, uses a unit once CORE-02 exists. Before that, area may be omitted. This feature does not block on CORE-02: if area is entered before units exist, the form waits until CORE-02 rather than storing a free-text unit. The first release of PROD-01 may ship without the area fields and add them with CORE-02.

## User Interactions

- Create a quinta, then a vidriera, and land on the vidriera detail.
- Rename a cantero label.
- Deactivate a quinta, vidriera, or cantero.
- The vidriera detail is reachable in one step from the farm list.

## Acceptance Criteria

- [ ] Creating a vidriera persists the vidriera and exactly four canteros.
- [ ] The four canteros have distinct labels and are visible on the vidriera detail.
- [ ] A second vidriera with the same name in the same quinta is rejected.
- [ ] The same vidriera name is accepted in a different quinta.
- [ ] A duplicate cantero label inside one vidriera is rejected.
- [ ] Deactivating a vidriera removes it from the default active list and leaves the record readable by direct navigation.
- [ ] Deleting a vidriera that has canteros through this feature's own creation path is rejected; deactivation is the offered action.
- [ ] The detail view is usable at a desktop width of at least 1280 pixels.

## Edge Cases & Validation

- Empty names are rejected.
- Leading and trailing spaces are not significant for uniqueness.
- A quinta with no vidrieras is a valid empty state and explains how to add the first one.

## Out of Scope

- Cultivation cycles (PROD-03).
- Maps and geometry.
- A variable number of canteros. The confirmed structure is four.
- Medianero assignment (PROD-05).

## Dependencies & Integration Points

- CORE-01 for access.
- PROD-03, OPS-01, and TRACE-01 extend the vidriera detail.
- Domain model: [PRODUCTION_MODEL.md](../domain/PRODUCTION_MODEL.md).

## Open Questions

- [OQ-21](../OPEN_QUESTIONS.md#oq-21) is resolved. A vidriera has four canteros.
