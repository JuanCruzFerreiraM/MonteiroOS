# PROD-01 — Farms, Vidrieras & Beds

## Metadata
- ID: PROD-01
- Module: Production
- Stage: 1
- Status: In Progress
- Priority: P0
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: CORE-01

## Objective

Represent the physical production hierarchy and give each quinta, vidriera, and cantero a stable identity that later records can point at.

## Business Value

Every operation and harvest needs a stable place. The vidriera is the place the business manages day to day. People need a short code they can say and write, separate from the internal identifier and from any later map.

## Functional Description

The operator creates quintas and, within each, vidrieras. Creating a vidriera also creates four canteros, numbered 1 through 4. The vidriera detail view shows the quinta, the operational code, the four canteros, and an empty region where the active cycle and recent activity will appear in later features.

Each quinta and each vidriera has three distinct facts:

1. An immutable technical identifier, used for persistence and relationships.
2. A stable operational code, used by people in everyday work.
3. A descriptive name or location reference, which may be edited.

Villa Elisa and Arturo Seguí are not seeded as a hidden fixture. The examples `VE` and `AS` illustrate the code convention only. The business creates the properties it uses. Tests may create their own names and codes.

Optional measured area may be stored on a vidriera or a cantero. Empty area means unknown, not zero. A measured area is not a map polygon and is not calculated from one.

This feature does not draw maps and does not store geographic boundaries. [PROD-06](PROD-06-farm-visual-mapping.md) attaches optional geometry to the records created here. PROD-01 remains valid when that feature is absent, and a record remains valid when it has no geometry.

## Expected Behavior

- The user can list quintas, open one, and see its vidrieras.
- The user can open a vidriera and see its canteros.
- Creating a quinta requires a unique operational code and a descriptive name.
- Creating a vidriera suggests the next operational code for that quinta. The suggestion is visible before save. Saving does not renumber any existing vidriera.
- Two quintas cannot share an operational code, including after one is deactivated.
- Two vidrieras cannot share an operational code. The numeric part is also unique within the parent quinta, including after deactivation.
- Two vidrieras in the same quinta cannot share a descriptive name.
- The same descriptive name is accepted in a different quinta.
- Each cantero keeps its number. Its displayed identifier is derived from the parent vidriera and that number.
- Deactivating a quinta or vidriera hides it from new selections, keeps it readable, and does not release its code.
- A vidriera or cantero that later has history cannot be deleted.
- Editing a descriptive name does not change the technical identifier or the operational code, and does not rewrite historical records.
- Moving a vidriera to another quinta is not offered as a rename. That change would redefine which property the section belongs to and would collide with the code convention. PROD-01 rejects it. History stays attached to the original technical identifier.

## Business Rules

- The physical hierarchy is quinta, then vidriera, then cantero. It does not depend on cultivation cycles, planted varieties, personnel, or geographic representation. See [PRODUCTION_MODEL.md](../domain/PRODUCTION_MODEL.md).
- Each vidriera has exactly four canteros. See [PRODUCTION_MODEL.md](../domain/PRODUCTION_MODEL.md).
- There is no maximum number of vidrieras in a quinta.
- Technical identifiers are assigned once and never change. They are not shown as the everyday name.
- Operational codes are assigned at creation, stored in uppercase, and compared without regard to case or surrounding spaces. They are not edited later and are not reused after deactivation.
- A quinta code is a short business code, two to twelve characters, using letters and digits, starting with a letter. `VE` and `AS` are examples, not fixtures.
- A vidriera code is `{quinta code}-V` plus a positive integer, padded to at least three digits: `VE-V001`, `VE-V002`, `AS-V001`. Numbers above 999 stay intact (`VE-V1000`). The number does not encode a physical position or a map order.
- The next suggested number is one greater than the highest number ever assigned in that quinta. Gaps are not filled.
- A cantero's human-readable identifier is `{vidriera code}-C{n}`, for example `VE-V001-C1` through `VE-V001-C4`. That label is derived. The cantero's technical identifier does not depend on it. An optional descriptive name may be edited and must stay unique within the vidriera when present.
- A descriptive location is not a key. Changing it leaves identity and history in place.
- Area is optional and is never inferred.

## Data Requirements

| Fact | Required |
| --- | --- |
| Quinta technical identifier | Yes, assigned by the system, immutable |
| Quinta operational code, unique across quintas, not reused | Yes |
| Quinta descriptive name | Yes |
| Quinta notes or location description | No |
| Quinta active flag | Yes |
| Vidriera technical identifier | Yes, assigned by the system, immutable |
| Vidriera operational code, unique, not reused | Yes |
| Vidriera descriptive name, unique within the quinta | Yes |
| Vidriera notes or location description | No |
| Vidriera active flag | Yes |
| Vidriera measured area and area unit | No |
| Cantero technical identifier | Yes, assigned by the system, immutable |
| Cantero number, 1–4, unique within the vidriera | Yes |
| Cantero descriptive name | No |
| Cantero active flag | Yes |
| Cantero measured area and area unit | No |

Area, when present, uses a unit once CORE-02 exists. Before that, area may be omitted. This feature does not block on CORE-02: if area is entered before units exist, the form waits until CORE-02 rather than storing a free-text unit. The first release of PROD-01 may ship without the area fields and add them with CORE-02.

Geographic coordinates are not facts of this feature.

## User Interactions

- Create a quinta with its code and name, then a vidriera, and land on the vidriera detail.
- Accept or, before the first save, replace the suggested vidriera code with another unused code that follows the convention.
- Edit a descriptive name or location note.
- Deactivate a quinta, vidriera, or cantero.
- The vidriera detail is reachable in one step from the farm list.

## Acceptance Criteria

- [ ] Creating a vidriera persists the vidriera and exactly four canteros numbered 1, 2, 3, and 4.
- [ ] The vidriera detail shows the operational code and the derived cantero labels `C1` through `C4`.
- [ ] A quinta code that matches an existing code after trimming and uppercasing is rejected, including when the existing quinta is inactive.
- [ ] A vidriera code that was used by a deactivated vidriera is rejected.
- [ ] The suggested vidriera code uses the next number after the highest ever assigned in that quinta, and saving it does not change any other vidriera's code.
- [ ] A second vidriera with the same descriptive name in the same quinta is rejected.
- [ ] The same descriptive name is accepted in a different quinta.
- [ ] Editing a descriptive name leaves the technical identifier, the operational code, and existing historical links unchanged.
- [ ] Changing a vidriera's parent quinta through the edit form is rejected.
- [ ] A duplicate cantero number inside one vidriera is rejected.
- [ ] Deactivating a vidriera removes it from the default active list and leaves the record readable by direct navigation.
- [ ] Deleting a vidriera that has canteros through this feature's own creation path is rejected; deactivation is the offered action.
- [ ] The detail view is usable at a desktop width of at least 1280 pixels.
- [ ] A quinta and a vidriera can be saved and reopened without a geographic boundary.

## Edge Cases & Validation

- Empty names and empty codes are rejected.
- Leading and trailing spaces are not significant. Codes are stored uppercase. Internal spaces in a code are rejected.
- A code that does not match the convention is rejected with the expected pattern named in the message.
- A quinta with no vidrieras is a valid empty state and explains how to add the first one.
- Suggesting a code never overwrites a code that has already been saved.
- The sequence does not depend on list order, map position, or which vidrieras are active.

## Out of Scope

- Cultivation cycles (PROD-03).
- Map rendering, polygon drawing, and geographic storage ([PROD-06](PROD-06-farm-visual-mapping.md)).
- A variable number of canteros. The confirmed structure is four.
- A cap on how many vidrieras a quinta may have.
- Reassigning an existing vidriera to another quinta.
- Medianero assignment (PROD-05).

## Dependencies & Integration Points

- CORE-01 for the shell. This feature does not depend on PROD-06.
- PROD-06 consumes these records and attaches optional geometry. It must not create a second quinta or vidriera entity.
- PROD-03, OPS-01, and TRACE-01 extend the vidriera detail and reference the technical identifier.
- Domain model: [PRODUCTION_MODEL.md](../domain/PRODUCTION_MODEL.md).

## Current implementation

This branch is in progress. It is not integrated and the acceptance criteria above are not marked complete.

The HTTP API lives at `/api/production`. Technical identifiers are UUID primary keys. Operational codes are separate columns and are not foreign keys. A vidriera and its four canteros are inserted in one transaction. Measured area is omitted until CORE-02, so this release does not store a free-text unit. Geographic columns are omitted until PROD-06. The existing primary keys and parent foreign keys are the records that feature will extend.

Lists hide inactive records unless `include_inactive=true`. Detail routes still return an inactive record. There is no delete route.

The tables come from Alembic revision `0001_production_hierarchy`. The application does not create them on startup. Before the upgrade, Production routes return `503` and the screens show that message. They do not show an empty quinta list. `GET /health` still reports database connectivity.

## Open Questions

- [OQ-21](../OPEN_QUESTIONS.md#oq-21) is resolved. A vidriera has four canteros.
