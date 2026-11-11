# Open questions

Unresolved business questions, plus decisions that used to be open and are now confirmed. A feature may proceed when every question it depends on is answered or marked non-blocking for the behavior that feature implements.

Blocking means the named behavior should wait. Non-blocking means the specification already defines a safe behavior.

Do not convert an open question into a rule inside code.

## Summary

| ID | Topic | Importance | Status |
| --- | --- | --- | --- |
| [OQ-01](#oq-01) | Several varieties in one cantero | High | Resolved: yes |
| [OQ-02](#oq-02) | How to measure a variety's share of a cantero | High | Open, non-blocking |
| [OQ-03](#oq-03) | Meaning of harvest progress | High | Open, non-blocking |
| [OQ-04](#oq-04) | Which harvest measurements are practical | High | Open, non-blocking |
| [OQ-05](#oq-05) | Quality classifications | High | Open, non-blocking |
| [OQ-06](#oq-06) | How application quantities are recorded today | Medium | Open, non-blocking |
| [OQ-07](#oq-07) | Useful lighting details | Medium | Open, non-blocking |
| [OQ-08](#oq-08) | Observed versus programmed light | Medium | Open, blocks device truth only |
| [OQ-09](#oq-09) | Useful nylon-covering details | Medium | Open, non-blocking |
| [OQ-10](#oq-10) | Heating procedure | Medium | Open, non-blocking |
| [OQ-11](#oq-11) | Extra labor types | Low | Open, non-blocking |
| [OQ-12](#oq-12) | Medianero master data | Medium | Open, non-blocking |
| [OQ-13](#oq-13) | Who bears input cost | High | Open for responsibility; purchasing is usually Monteiro |
| [OQ-14](#oq-14) | Medianero cost-sharing | High | Open, blocking for splits |
| [OQ-15](#oq-15) | Mixing before boxing | High | Open, non-blocking if origin can be partial or unknown |
| [OQ-16](#oq-16) | Boxes and production origin | High | Open, blocking for a mandatory origin |
| [OQ-17](#oq-17) | Sales records and settlements | High | Open, blocking for settlements |
| [OQ-18](#oq-18) | Existing stock records | Medium | Open, blocking for an imported opening balance |
| [OQ-19](#oq-19) | Storage layout | Medium | Open, non-blocking |
| [OQ-20](#oq-20) | Users and devices | Medium | Resolved for the MVP: one desktop user |
| [OQ-21](#oq-21) | Bed count | Medium | Resolved: four canteros |
| [OQ-22](#oq-22) | Simultaneous medianeros | Medium | Resolved: one medianero or direct management |
| [OQ-23](#oq-23) | Work between cycles | Medium | Open, non-blocking |
| [OQ-24](#oq-24) | Box identity beyond the letter | Medium | Open, non-blocking |
| [OQ-25](#oq-25) | Irrigation without a water volume | Medium | Open, non-blocking |
| [OQ-26](#oq-26) | Commercial presentations | High | Open, non-blocking |
| [OQ-27](#oq-27) | Reports for the first pilot | Medium | Open, non-blocking |
| [OQ-28](#oq-28) | Separate portions of one variety and color | Medium | Open, non-blocking |

## Resolved

<a id="oq-01"></a>
### OQ-01 — Can multiple varieties occupy one cantero at the same time?

- Affected features: [PROD-04](features/PROD-04-crop-allocation.md), [HARV-01](features/HARV-01-partial-harvest.md)
- Importance: High
- Blocking: None. Resolved.
- Current knowledge: Yes. A cantero can contain multiple varieties in one cultivation cycle. The system must not enforce one variety per bed.
- Required validation: None for the rule. How the share is measured remains [OQ-02](#oq-02).

<a id="oq-20"></a>
### OQ-20 — Who will enter operations, and on which devices?

- Affected features: [CORE-01](features/CORE-01-application-foundation.md)
- Importance: Medium
- Blocking: None for the MVP. Resolved as a product decision.
- Current knowledge: The MVP is one software user on a desktop. Mobile interfaces and multi-user access are future evolution, not Stages 1–4. Business people are not accounts.
- Required validation: None before the first flow. Which person sits at the desk can be noted during the pilot.

<a id="oq-21"></a>
### OQ-21 — Does every vidriera always have exactly four canteros?

- Affected features: [PROD-01](features/PROD-01-farms-vidrieras-beds.md)
- Importance: Medium
- Blocking: None. Resolved.
- Current knowledge: Yes. The confirmed hierarchy gives each vidriera four canteros.
- Required validation: None.

<a id="oq-22"></a>
### OQ-22 — Can more than one medianero be assigned to the same vidriera at once?

- Affected features: [PROD-05](features/PROD-05-medianero-assignment-history.md)
- Importance: Medium
- Blocking: None. Resolved.
- Current knowledge: No. A vidriera has one open medianero assignment or is directly managed by Monteiro. Historical intervals are kept. Direct management does not invent a person.
- Required validation: None.

## Open

<a id="oq-02"></a>
### OQ-02 — How should a variety's occupied portion of a cantero be measured?

- Affected features: [PROD-04](features/PROD-04-crop-allocation.md)
- Importance: High
- Blocking: Non-blocking. An allocation is valid without a measured share. A free-text note is allowed and is not treated as area, length, or plant count.
- Current knowledge: Multiple varieties per cantero are confirmed. The measure is not. Candidates are surface area, linear meters, plant count, or a combination.
- Required validation: Walk a mixed bed and record how people describe each variety's share before storing a numeric portion.

<a id="oq-03"></a>
### OQ-03 — How precisely should partial harvest progress be defined?

- Affected features: [HARV-01](features/HARV-01-partial-harvest.md), [HARV-03](features/HARV-03-yield-indicators.md)
- Importance: High
- Blocking: Non-blocking for storing a progress note. Blocking for using that note as area, plants, or a completed bed.
- Current knowledge: Cuts are repeated and partial. A percentage may mean area, plants, or a rough estimate. Those meanings are not interchangeable.
- Required validation: Ask harvesters what a progress figure meant on a recent cut.

<a id="oq-04"></a>
### OQ-04 — Which measurements are practical during harvest?

- Affected features: [HARV-02](features/HARV-02-harvest-measurements-quality.md), [HARV-03](features/HARV-03-yield-indicators.md)
- Importance: High
- Blocking: Non-blocking. Ramo and vara are both available. No global conversion is applied.
- Current knowledge: The business uses both ramo (bunch) and vara (stem). Which one is practical for each flower, and when a count is estimated, is not documented.
- Required validation: Observe one harvest and record the unit people actually count.

<a id="oq-05"></a>
### OQ-05 — What quality classifications are actually used?

- Affected features: [HARV-02](features/HARV-02-harvest-measurements-quality.md)
- Importance: High
- Blocking: Non-blocking for an empty, user-maintained catalog. Blocking for a seeded class list.
- Current knowledge: Quality is separate from commercial size. Class names are not documented.
- Required validation: Collect the classes used at harvest or packing. Do not invent names.

<a id="oq-06"></a>
### OQ-06 — How are product application quantities recorded today?

- Affected features: [OPS-02](features/OPS-02-operation-types.md), [INV-01](features/INV-01-product-catalog.md)
- Importance: Medium
- Blocking: Non-blocking. An application line requires a product, a quantity, and a catalog unit when the quantity is known. The operation can still be saved under OPS-01 without lines.
- Current knowledge: Applications use fertilizers and crop-protection products. The field unit is not documented.
- Required validation: Review a recent mix with the person who prepared it.

<a id="oq-07"></a>
### OQ-07 — What operation-specific details are useful for lighting?

- Affected features: [OPS-02](features/OPS-02-operation-types.md)
- Importance: Medium
- Blocking: Non-blocking for a manual record that distinguishes a program from an observed occurrence. Blocking for device integration.
- Current knowledge: Lighting is a vidriera-level operation. The useful extra fields, beyond the program-or-observed flag and an interval, are not documented.
- Required validation: Record one lighting change and note which details the operator would want to see later.

<a id="oq-08"></a>
### OQ-08 — Are lighting states observable or only programmed?

- Affected features: [OPS-02](features/OPS-02-operation-types.md)
- Importance: Medium
- Blocking: Blocking for treating a program as an occurrence. Non-blocking for storing the two facts separately.
- Current knowledge: A schedule is not proof that the lights ran. Whether anyone can see the real state is unknown.
- Required validation: Confirm whether operators observe the lights or only trust the timer.

<a id="oq-09"></a>
### OQ-09 — What operation-specific details are useful for black nylon covering?

- Affected features: [OPS-02](features/OPS-02-operation-types.md)
- Importance: Medium
- Blocking: Non-blocking for a raise or lower event, or a covered/exposed interval.
- Current knowledge: Covering changes at vidriera level. Richer procedure fields are not documented.
- Required validation: Record one covering cycle and the times that are actually known.

<a id="oq-10"></a>
### OQ-10 — What is the operating procedure for cold-protection heating?

- Affected features: [OPS-02](features/OPS-02-operation-types.md)
- Importance: Medium
- Blocking: Non-blocking for activation time, duration, and a free-text note. Blocking for sensor-derived context.
- Current knowledge: Heating is called *dar fuego*. The control routine is not documented.
- Required validation: Describe how heating is started and stopped.

<a id="oq-11"></a>
### OQ-11 — Which additional manual operations are worth tracking?

- Affected features: [OPS-02](features/OPS-02-operation-types.md)
- Importance: Low
- Blocking: Non-blocking. Manual labor can be saved with a task description.
- Current knowledge: No further task list is confirmed.
- Required validation: Review free-text task names after a period of use.

<a id="oq-12"></a>
### OQ-12 — What information does the business retain about each medianero?

- Affected features: [CORE-03](features/CORE-03-people-and-roles.md), [PROD-05](features/PROD-05-medianero-assignment-history.md)
- Importance: Medium
- Blocking: Non-blocking for a name. Blocking for additional required profile fields.
- Current knowledge: Medianeros are production partners. No master-data list is in the repository.
- Required validation: Ask which fields are already written down.

<a id="oq-13"></a>
### OQ-13 — Who bears the cost of inputs used on medianero vidrieras?

- Affected features: [COST-02](features/COST-02-production-cost-allocation.md), [INV-04](features/INV-04-suppliers-purchasing.md)
- Importance: High
- Blocking: Blocking for a default economic responsibility. Non-blocking for recording the business as the usual purchaser.
- Current knowledge: Monteiro generally purchases agricultural inputs and other production materials. Purchasing does not decide economic responsibility. The share a medianero bears is [OQ-14](#oq-14).
- Required validation: For one medianero vidriera, trace a recent product from purchase to application and note who bore the cost. Do not infer it from the invoice alone.

<a id="oq-14"></a>
### OQ-14 — What financial agreements govern medianero cost-sharing?

- Affected features: [COST-02](features/COST-02-production-cost-allocation.md), [COST-03](features/COST-03-unit-economics.md)
- Importance: High
- Blocking: Blocking for any automatic split, settlement, or margin attributed to a medianero.
- Current knowledge: No formula is documented. [ADR 0006](decisions/0006-medianero-financial-rules-deferred.md) forbids inventing one.
- Required validation: Document the arrangement with the owner before any feature divides money.

<a id="oq-15"></a>
### OQ-15 — Are harvests from different vidrieras mixed before box preparation?

- Affected features: [COMM-01](features/COMM-01-harvest-lots-boxes.md)
- Importance: High
- Blocking: Non-blocking. A line can be exact, partial, or unknown. Quantities are not distributed without evidence.
- Current knowledge: Mixing is possible. It is not confirmed as the normal practice.
- Required validation: Watch box preparation and record whether one box can contain more than one vidriera.

<a id="oq-16"></a>
### OQ-16 — How are harvest boxes linked to individual production origins?

- Affected features: [COMM-01](features/COMM-01-harvest-lots-boxes.md), [COMM-05](features/COMM-05-commercial-traceability.md)
- Importance: High
- Blocking: Blocking for a mandatory vidriera or cycle on every box. Non-blocking for exact, partial, and unknown origin.
- Current knowledge: The medianero letter does not identify the vidriera. The practical precision of a better link is unknown.
- Required validation: Take a recent box and see whether anyone can name the cycle, vidriera, or cantero.

<a id="oq-17"></a>
### OQ-17 — How are sales, payments, and medianero settlements recorded?

- Affected features: [COMM-04](features/COMM-04-sales-receipts.md), [COST-03](features/COST-03-unit-economics.md)
- Importance: High
- Blocking: Blocking for settlements. Non-blocking for a sale with quantities, classifications, prices, and receipts.
- Current knowledge: Flowers are sold wholesale. Prices may depend on variety, size, color, and presentation. The current paper records and any settlement are not documented.
- Required validation: Review the notes used after a market day.

<a id="oq-18"></a>
### OQ-18 — What minimum inventory information already exists?

- Affected features: [INV-03](features/INV-03-stock-movements.md)
- Importance: Medium
- Blocking: Blocking for an imported opening balance. Non-blocking for explicit receipts and adjustments.
- Current knowledge: No inventory dataset is in the repository.
- Required validation: Decide with the business whether any existing list is trustworthy enough to enter as adjustments.

<a id="oq-19"></a>
### OQ-19 — What are the storage areas and how are they organized?

- Affected features: [INV-02](features/INV-02-storage-locations.md)
- Importance: Medium
- Blocking: Non-blocking. Locations are user-entered.
- Current knowledge: Names and nesting are not documented.
- Required validation: Walk the storage areas and record the names people use.

<a id="oq-23"></a>
### OQ-23 — How should work between cycles be classified?

- Affected features: [OPS-01](features/OPS-01-operation-registration.md), [PROD-03](features/PROD-03-cultivation-cycles.md)
- Importance: Medium
- Blocking: Non-blocking. An operation can be saved with no cycle.
- Current knowledge: Preparation must not be forced onto an unrelated cycle. The local name for that work is not documented.
- Required validation: Ask what operators call bed preparation and whether they see it as part of the next cycle.

<a id="oq-24"></a>
### OQ-24 — What identifies a commercial box besides the medianero letter?

- Affected features: [COMM-01](features/COMM-01-harvest-lots-boxes.md)
- Importance: Medium
- Blocking: Non-blocking. A box has an explicit identifier. Letters are not assumed unique over time.
- Current knowledge: Letters associated with medianeros are the known mark. The letter is not an origin.
- Required validation: Inspect current boxes and record every mark used on a market day.

<a id="oq-25"></a>
### OQ-25 — How should irrigation amounts be recorded when water volume is unavailable?

- Affected features: [OPS-02](features/OPS-02-operation-types.md)
- Importance: Medium
- Blocking: Non-blocking. Duration, or a start and end, is enough. Volume is optional.
- Current knowledge: Irrigation is a timed vidriera-level operation. A measured volume is not confirmed.
- Required validation: Ask whether any irrigation is measured in liters, and what is written down when it is not.

<a id="oq-26"></a>
### OQ-26 — What commercial presentations are used for each flower type?

- Affected features: [PROD-02](features/PROD-02-crop-variety-catalog.md), [HARV-02](features/HARV-02-harvest-measurements-quality.md), [COMM-04](features/COMM-04-sales-receipts.md)
- Importance: High
- Blocking: Non-blocking. A presentation is optional. A vara count is stored only when a presentation explicitly declares one.
- Current knowledge: Some chrysanthemum presentations may use a defined number of varas per ramo. Other products do not. No list is documented, and no count is confirmed.
- Required validation: For each flower type that is packed, record the presentation name and, only if the business states one, the vara count.

<a id="oq-27"></a>
### OQ-27 — Which reports are most valuable during the first operational pilot?

- Affected features: [TRACE-01](features/TRACE-01-production-activity-history.md), [HARV-04](features/HARV-04-cycle-comparison.md)
- Importance: Medium
- Blocking: Non-blocking. Vidriera history and, later, cycle comparison are already specified.
- Current knowledge: The pilot needs to answer what was done and, once harvest exists, what was cut. A broader report list is not prioritized.
- Required validation: After the first weeks of entries, ask which question the history screen did not answer.

<a id="oq-28"></a>
### OQ-28 — When do physically separate portions of the same variety need their own allocations?

- Affected features: [PROD-04](features/PROD-04-crop-allocation.md), [HARV-01](features/HARV-01-partial-harvest.md)
- Importance: Medium
- Blocking: Non-blocking. The first version stores one logical allocation per variety and color on a cantero and cycle.
- Current knowledge: A cantero may hold several varieties. Treating one variety and color as one row is a simplification. It is not a claim that two separate plantings of that combination cannot exist in the same bed.
- Required validation: Ask whether operators need to tell those portions apart before yield is compared at a finer grain than the cantero. Historical rows must remain readable if separate identities are added later. Do not add bed geometry to answer this.
