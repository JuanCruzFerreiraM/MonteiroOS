# CORE-02 — Units of Measurement

## Metadata
- ID: CORE-02
- Module: Measurement
- Stage: 1
- Status: Planned
- Priority: P1
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: CORE-01

## Objective

Store every quantity against a controlled unit so later records can be compared and converted only when the conversion is valid.

## Business Value

Free-text units make yield and cost impossible to reconcile. A shared catalog lets applications, harvests, stock, and costs use the same language.

## Functional Description

Maintain dimensions and units. A quantity in any later feature references a unit; it does not store an arbitrary unit string.

The initial catalog includes the dimensions volume, mass, time, area, temperature, count, and concentration or application rate, and the example units mL, L, g, kg, minutes, hours, m², hectares, plants, vara (stem), ramo (bunch), mL/L, g/L, and kg/ha. Standard factors between units in the same physical system, such as mL and L, are part of the catalog.

Vara and ramo are distinct count units. The catalog has no factor between them. Some commercial presentations may later declare an explicit number of varas per ramo. That declaration lives on the presentation in PROD-02. It is not a unit-catalog conversion, and it is never applied unless that presentation is the one recorded on the measurement.

Users who maintain reference data can add a unit inside an existing dimension. They cannot place a unit in two dimensions or define a conversion that crosses dimensions.

## Expected Behavior

- Selecting a unit for a quantity offers only active units.
- Converting 1000 mL yields 1 L.
- A request to convert g to L is rejected.
- A request to convert ramo (bunch) to vara (stem), or the reverse, is rejected.
- Deactivating a unit removes it from new selections and leaves existing references readable.
- Deleting a referenced unit is rejected.

## Business Rules

- A unit belongs to exactly one dimension.
- Conversion is allowed only inside a dimension, and only when a defined factor or an affine temperature conversion exists.
- Ramo and vara have no global conversion. See [ADR 0008](../decisions/0008-controlled-measurement-units.md).
- Rate units such as mL/L do not convert to a bare volume without additional data this feature does not store.

## Data Requirements

| Fact | Required |
| --- | --- |
| Dimension name | Yes |
| Unit code and display name | Yes |
| Dimension | Yes |
| Conversion to a chosen reference unit within the dimension, when a conversion exists | Required for units that support conversion; absent for plants, vara, and ramo |
| Active flag | Yes |

## User Interactions

- Browse units by dimension.
- Add a unit, providing its dimension and, when relevant, its factor.
- Deactivate a unit.

Daily operation forms do not require the user to manage the catalog. They only pick a unit.

## Acceptance Criteria

- [ ] A quantity cannot be saved with a unit code that is not in the catalog.
- [ ] mL converts to L by the seeded factor, and g converts to kg by the seeded factor.
- [ ] Converting a mass unit to a volume unit fails with a validation error.
- [ ] The catalog includes ramo and vara as separate count units, with those Spanish names visible.
- [ ] Converting ramo, vara, or plants among each other fails.
- [ ] Saving a commercial presentation does not create a ramo-to-vara factor in this catalog.
- [ ] An inactive unit remains visible on a record that already uses it and is absent from the default picker.
- [ ] A unit that is referenced cannot be deleted.
- [ ] The seeded catalog contains the example units listed in this specification and no global ramo-to-vara factor.

## Edge Cases & Validation

- A factor of zero or a negative factor is rejected for multiplicative conversions.
- Two units with the same code are rejected.
- Temperature is not given a fake multiplicative factor.

## Out of Scope

- A global or automatic conversion between ramo and vara. An explicit count on one presentation is PROD-02.
- Converting an application rate into a total mass without a recorded carrier volume or area.
- Localization of unit names beyond a stable code and a display name.

## Dependencies & Integration Points

- CORE-01 for access.
- INV-01, OPS-02, HARV-02, INV-03, and cost features reference these units.
- Domain rules: [INVENTORY_MODEL.md](../domain/INVENTORY_MODEL.md#units).

## Open Questions

None. How the business measures today is [OQ-04](../OPEN_QUESTIONS.md#oq-04) and [OQ-06](../OPEN_QUESTIONS.md#oq-06). Those questions do not change the catalog rules.
