# Inventory, units, and cost concepts

Products, stock, and money are easy to collapse into one record. This document keeps them apart. Commercial sales are in [COMMERCIAL_TRACEABILITY.md](COMMERCIAL_TRACEABILITY.md).

<a id="units"></a>

## Units

### Confirmed

Quantities use a controlled unit catalog. A user does not type an arbitrary unit string into an operation, harvest, stock movement, or cost.

Dimensions to support:

- Volume
- Mass
- Time
- Area
- Temperature
- Count
- Concentration and application rate

Examples of units the catalog must be able to hold: mL, L, g, kg, minutes, hours, m², hectares, plants, vara (stem), ramo (bunch), mL/L, g/L, and kg/ha.

Conversions must be dimensionally valid. A mass does not convert to a volume. Plants, vara, and ramo do not convert into each other inside the unit catalog. A commercial presentation may declare an explicit number of varas per ramo for that presentation only. There is no universal factor. The controlled unit catalog is part of the first MVP.

The same unit catalog serves operations, harvests, inventory, and costs.

### Working assumptions

- Standard SI-style factors may be seeded for units that have an agreed physical relationship, such as 1 L = 1000 mL and 1 kg = 1000 g. These are unit-system facts, not Monteiro operating data.
- Temperature, if converted, uses an affine conversion. It is not a multiplication factor.
- Rate units such as mL/L, g/L, and kg/ha belong to their own dimensions. They do not convert into a bare mass or volume without a separate volume, mass, or area.
- A unit that is already referenced can be deactivated and cannot be deleted.

## Product catalog

### Confirmed

Cultivation products live in a reusable catalog. While recording an application, the user searches that catalog. If the product is missing, they can create it without leaving the application. Possible duplicates are shown before creation.

A product may record:

| Information | Required |
| --- | --- |
| Commercial name | Yes |
| Manufacturer | No |
| Category | Yes, from an extensible list |
| Formulation or composition | No |
| Presentation | No |
| Standard quantity unit | Yes, from the unit catalog |
| Identification or regulatory information | No |
| Active or inactive | Yes |

The catalog does not invent regulatory duties or application recommendations for crop-protection products. Optional identification text is stored when the business has it.

A product is not a stock item, a quantity on hand, a storage location, an inventory movement, or a consumption record.

### Working assumptions

- Categories start small enough to filter products, including labels for fertilizer and crop protection, and the business can add categories. The list is not a regulatory classification.
- Inactive products stay on historical applications and disappear from default search.

### Unknowns

How quantities are recorded in the field today is [OQ-06](../OPEN_QUESTIONS.md#oq-06). The software still requires a catalog unit; it does not wait for that answer to store a quantity.

## Stock and purchasing

### Confirmed

Stock is a later concern than the catalog. Stage 1 only needs the catalog so applications can name a product.

When inventory arrives, it must distinguish:

- the catalog product;
- the quantity recorded on an application;
- a confirmed withdrawal from a storage location;
- a purchase from a supplier.

An application quantity does not silently reduce stock. Nobody has established that the business has an accurate opening inventory. Stock therefore starts from explicit receipts or adjustments, not from an assumed balance.

### Unknowns

- What inventory information already exists ([OQ-18](../OPEN_QUESTIONS.md#oq-18)).
- What the storage areas are and how they are organized ([OQ-19](../OPEN_QUESTIONS.md#oq-19)).
- Who buys products used on medianero vidrieras ([OQ-13](../OPEN_QUESTIONS.md#oq-13)).

Locations and suppliers are entered by users. None are seeded.

<a id="costs"></a>

## Costs

### Confirmed

The long-term aim is production cost and commercial margin per bunch.

Cost categories that may appear:

- Agricultural products
- Labor
- Water
- Energy
- Materials
- Packaging
- Transportation
- Shared overhead

Direct costs and indirect costs are different. Physical consumption and economic responsibility are different. A recorded actual cost and an estimate are different, and the record must say which one it is.

Monteiro generally purchases inputs. The purchaser, the place or operation that consumed them, and the party that bears the cost are three facts. Cost-sharing with medianeros is unknown and must not be given a default split. Purchasing does not fill economic responsibility.

### Working assumptions

- If a price is missing, the cost is unknown. It is not stored as zero.
- A shared cost may sit on a quinta or on several vidrieras without being divided until an allocation method is chosen and stored with the result.
- Currency is part of every monetary amount. The entry default is ARS because the business operates in Argentina. The user can change it. No prices are seeded.

### Unknowns

[OQ-13](../OPEN_QUESTIONS.md#oq-13), [OQ-14](../OPEN_QUESTIONS.md#oq-14), and [OQ-17](../OPEN_QUESTIONS.md#oq-17) block settlement and automatic responsibility. They do not block recording a product quantity or an explicitly sourced unit cost.
