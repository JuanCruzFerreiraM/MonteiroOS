# Commercial traceability

This document describes how flowers leave the farm and how that movement can point back to production. It does not specify an accounting system.

## Confirmed

Flowers go to the wholesale market in boxes. Boxes are currently identified with letters associated with medianeros. That letter gives some commercial traceability. It does not establish the cultivation origin. Flowers in a box may have come from a known vidriera, from several, or from an origin the business can no longer identify.

The future system links harvest batches and box contents to production cycles and physical origins when the link is known. Origin is one of three states: exact, partial, or unknown. Partial origin records the parts that are known and does not divide the quantity across the remaining vidrieras. A medianero letter never fills the missing parts.

A sale eventually needs a quantity, a unit, and a price so the business can compare revenue with production cost per bunch. Production cost and commercial cost, such as packaging and transport, stay distinguishable.

## Working assumptions

- A harvest lot groups one or more harvest events before or during packing. The lot is optional for a harvest event until packing starts.
- A box has an identifier. The current letter can be stored as that identifier, together with the medianero it is associated with when that association is known.
- Box contents name a variety and a quantity. Each content line may point at one or more harvest lots, or at unknown origin.
- A customer, an order, a dispatch, and a sale are separate records. An order does not decrement flower inventory. Agricultural-product stock and flowers for sale are different flows.
- A box is loaded on at most one dispatch.
- A sale may refer to an order and to dispatched boxes when those links exist. A receipt records money against a sale and may be partial.
- Currency is stored on every price and receipt. The entry default is ARS.
- Customer account behavior in Stage 4 is the outstanding amount of recorded sales minus recorded receipts. It is not a ledger of invoices, taxes, or credits beyond that.

## Unknowns

- Whether harvests are mixed across vidrieras before boxing ([OQ-15](../OPEN_QUESTIONS.md#oq-15)).
- How precisely a box can be tied to a cycle or vidriera ([OQ-16](../OPEN_QUESTIONS.md#oq-16)).
- How sales, payments, and medianero settlements are recorded today ([OQ-17](../OPEN_QUESTIONS.md#oq-17)).
- What else, besides the medianero letter, identifies a box ([OQ-24](../OPEN_QUESTIONS.md#oq-24)).

Until OQ-17 is answered, the software records sales and receipts and does not calculate a medianero settlement.

## Traceability rules

From a box, a user can see:

- the identifier and any associated medianero;
- the varieties and quantities on the box;
- each linked harvest lot, cycle, vidriera, and cantero;
- an explicit "origin unknown" or a list of several origins when that is the case.

From a cultivation cycle, a user can see the boxes whose contents link back to that cycle.

The medianero letter is always labeled as a commercial mark. The interface does not present it as the vidriera of origin.

<a id="cost-and-margin"></a>

## Cost and margin

Unit economics use the recorded unit, including the ramo, only when quantities were recorded in that unit or a valid dimensional conversion exists. A presentation-specific vara count is used only when the measurement cites that presentation, and the derived figure is labeled. There is no universal ramo-to-vara factor.

A sale price may differ by variety, commercial size, color, presentation, and unit. The price is stored on the sale. It is not assumed from the planting record.

Margin for a cycle, a lot, or a bunch is revenue minus known cost, in one currency. If either side is missing, the result is incomplete. Production costs and commercial costs are listed separately so a packaging cost is not presented as a growing cost.

Cost allocation rules themselves are in [INVENTORY_MODEL.md](INVENTORY_MODEL.md#costs).
