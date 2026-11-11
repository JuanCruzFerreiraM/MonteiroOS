# Glossary

Spanish terms used in the operation are kept in the product language. English in this table is the definition, not a replacement name in the interface.

| Term | Definition |
| --- | --- |
| Quinta | A physical production property. The current properties are Villa Elisa and Arturo Seguí. Highest level of the physical hierarchy. |
| Vidriera | The primary operational production section inside a quinta. Irrigation, product applications, and several environmental operations are shared across the vidriera. |
| Cantero | A cultivation bed inside a vidriera. Each vidriera has four. A cantero may hold several varieties at once. |
| Flower type | A commercial kind of flower, such as chrysanthemum. Botanical identity is optional. Also called a crop. |
| Variety | A commercial or local name for a specific flower variety. It belongs to a flower type. A botanical classification is optional. |
| Color | An independent classification. It may be known at planting and recorded again at harvest. |
| Commercial size | A harvest or sale grade, such as large, medium, or small for a given flower type. Not required at planting. Flower types do not share one size list. |
| Presentation | A commercial packing form for a flower type. It may declare an explicit number of varas per ramo for that presentation only. |
| Ramo | A bunch. A count unit. It does not convert to a vara unless a specific presentation says how many varas it contains. |
| Vara | A stem. A count unit, distinct from ramo. |
| Cultivation cycle | The temporal production cycle of one vidriera, from planting as a whole until the cycle is finalized. A vidriera has at most one active top-level cycle. |
| Crop allocation | The assignment of a variety, and optionally a color, to a cantero for one cultivation cycle. Several allocations may share a cantero. Commercial size is not part of the allocation. |
| Medianero | A production partner responsible for assigned production areas under an arrangement whose financial rules are not yet documented. Not an ordinary employee. |
| Employee | A person who performs work for the business as staff. |
| Operation performer | A person who carries out an operation. An operation may have several performers, or none. |
| Responsible person | A person accountable for an operation. This may differ from the performer and from the person who records it. |
| Direct management | A vidriera responsibility interval in which Monteiro manages the section and no medianero is assigned. |
| Operation | A recorded cultivation event or observation with a time, a type, and a physical scope. |
| Operation scope | The vidrieras an operation applies to. Scope is independent from the beds used to measure yield. |
| Product | A reusable catalog entry for something used in cultivation, such as a fertilizer or a crop-protection product. A product is not a stock quantity. |
| Stock | A quantity of a catalog product held at a storage location. |
| Inventory movement | A recorded change to stock: receipt, withdrawal, transfer, or adjustment. |
| Storage location | A named place where stock is held. |
| Measurement unit | A controlled unit from a catalog, belonging to one dimension. Quantities cannot store an arbitrary unit string. |
| Bunch | English for ramo. See ramo. |
| Observation | A record of conditions. It may include photographs. It does not by itself mean that someone intervened. |
| Harvest event | One cut of a variety in a cultivation cycle. The cantero is recorded when the origin is exact. The same variety and cantero may have many events. |
| Harvest measurement | A quantity, unit, and optional quality or discard attached to a harvest event. |
| Quality classification | A business-defined class for harvested flowers. The actual classes are not yet confirmed. |
| Commercially acceptable production | Harvested quantity that remains after discards, when both amounts were recorded in a compatible unit. |
| Harvest lot | A grouping of harvest events or quantities prepared to move toward sale. |
| Box | The container used to take flowers to the wholesale market. Boxes are currently identified with letters associated with medianeros. |
| Customer | A wholesale buyer. |
| Order | A customer's requested quantities. An order is not an invoice and not a stock withdrawal. |
| Dispatch | The loading of boxes onto transport for delivery. |
| Sale | A record of quantities sold and their prices. |
| Receipt | Money recorded against a sale. This is not a general-ledger entry. |
| Direct cost | A cost that is recorded against a specific operation, cycle, or vidriera. |
| Indirect cost | A shared cost that is not yet, or not fully, attributable to one cycle. |
| Economic responsibility | Who bears a cost. This is separate from who consumed the physical product. |
| Dar fuego | The local name for cold-protection heating. |

## Names that must stay distinct

- Quinta, vidriera, and cantero are physical. A cultivation cycle is temporal.
- A product catalog entry, a stock quantity, a storage location, a purchase, and an application are five different records.
- A medianero, an employee, a performer, a responsible person, and a recording person are business relationships. The MVP does not turn them into software accounts.
- Exact origin, partial origin, and unknown origin are different states. A medianero letter is none of them.
- A box letter identifies a commercial handling mark associated with a medianero. It does not by itself identify the vidriera that grew the flowers.
