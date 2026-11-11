# PROD-02 — Flower Type, Variety & Classifications

## Metadata
- ID: PROD-02
- Module: Production
- Stage: 1
- Status: Planned
- Priority: P1
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: CORE-01

## Objective

Maintain controlled catalogs for flower type, variety, color, commercial size, and commercial presentation, without collapsing harvest grades into the planted crop.

## Business Value

The same planting can be sold as different sizes and qualities. The catalog has to name what was planted separately from how a cut is graded and packed.

## Functional Description

Four classification concepts stay independent:

| Concept | When it is known | Example the model must be able to represent |
| --- | --- | --- |
| Flower type | Planting | Chrysanthemum |
| Variety | Planting | Snow, Palisade |
| Color | Planting, when known, and again at harvest | White, yellow |
| Commercial size | Harvest or sale | Large, medium, small |

Quality and commercial presentation are separate attributes. They are not varieties and they are not sizes.

A variety belongs to one flower type. Botanical classification is optional. Local names are valid. Search runs before create, and a similar name is shown before save.

Commercial sizes belong to one flower type. Chrysanthemum may have large, medium, and small while another flower type has a different list, or none. Colors are a reusable catalog. A flower type may associate the colors that apply to it. The system must be able to represent combinations such as Chrysanthemum / Snow / large / white and Chrysanthemum / Snow / medium / yellow. Those names are examples of shape, not seeded business data.

A commercial presentation belongs to one flower type. It may optionally declare an explicit number of varas (stems) per ramo (bunch) for that presentation only. The declaration is stored on the presentation, is visible wherever it is used, and is not copied into the unit catalog. Presentations without that number do not convert.

These catalogs are not planting records. PROD-04 uses flower type, variety, and optional color. Size, quality, and presentation are chosen on harvest and sale records.

Inactive entries stay on historical rows and drop out of the default picker.

No prices are stored here. Different sizes may later have different prices on sales (COMM-04).

## Expected Behavior

- A variety can be saved with a local name and no botanical name.
- Two varieties in the same flower type cannot share a commercial name, ignoring case and surrounding spaces.
- Two flower types can define different size lists.
- A presentation can be saved with no stem count.
- A presentation stem count, when present, is a positive integer scoped to that presentation.
- Deactivating a flower type hides its varieties, sizes, and presentations from new selections.

## Business Rules

- Cultivated identity is flower type, variety, and color when known. See [PRODUCTION_MODEL.md](../domain/PRODUCTION_MODEL.md).
- Commercial size is not part of cultivated identity.
- Do not assume every flower type uses the same sizes, colors, or presentations.
- A ramo and a vara do not gain a global conversion from this catalog. See [ADR 0008](../decisions/0008-controlled-measurement-units.md).

## Data Requirements

| Fact | Required |
| --- | --- |
| Flower type name | Yes |
| Flower type active flag | Yes |
| Variety commercial or local name | Yes |
| Variety flower type | Yes |
| Botanical classification | No |
| Variety active flag | Yes |
| Color name | Yes |
| Colors associated with a flower type | No |
| Commercial size name and flower type | Yes, on each size |
| Presentation name and flower type | Yes, on each presentation |
| Explicit varas per ramo on a presentation | No |

## User Interactions

- Maintain flower types, varieties, colors, sizes, and presentations from the catalog.
- Search before creating a variety, color, size, or presentation.
- From a later allocation, harvest, or sale form, create a missing entry without discarding the form, after the duplicate check.

## Acceptance Criteria

- [ ] Saving a variety with a commercial name and a flower type succeeds when the botanical field is empty.
- [ ] A second variety with the same commercial name and flower type is rejected.
- [ ] The create flow shows an existing variety with a similar name before confirming creation.
- [ ] One flower type can have sizes named large, medium, and small while another flower type has no sizes.
- [ ] A variety, a color, and a commercial size can be selected independently for the same flower type.
- [ ] A commercial presentation can be saved without a stem count.
- [ ] A presentation that declares varas per ramo stores that count only on that presentation.
- [ ] The unit catalog gains no ramo-to-vara conversion when a presentation is saved.
- [ ] An inactive variety remains readable from a historical allocation and is hidden from the default search.
- [ ] A variety, size, color, or presentation cannot be deleted while a historical record references it.
- [ ] A fresh database does not contain seeded varieties, colors, sizes, or prices.

## Edge Cases & Validation

- Empty names are rejected.
- A stem count of zero or less on a presentation is rejected.
- Deactivating a flower type leaves historical rows readable.

## Out of Scope

- Where a variety is planted (PROD-04).
- Harvest quantities and quality (HARV-02).
- Sale prices (COMM-04).
- A botanical taxonomy that users must complete.

## Dependencies & Integration Points

- CORE-01 for the application shell.
- PROD-04 uses flower type, variety, and color.
- HARV-02 and COMM-04 use size, color, quality, and presentation.
- CORE-02 owns units. This feature does not add unit conversions.

## Open Questions

- [OQ-26](../OPEN_QUESTIONS.md#oq-26) is non-blocking. Presentations can be added when known, including an explicit stem count when the business has one.
