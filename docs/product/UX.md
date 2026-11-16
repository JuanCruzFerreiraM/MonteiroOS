# Experience principles

## Intended product feel

Monteiro OS should feel like a modern desktop business application. The MVP is used by one person at a desk. Common tasks need short forms and few steps. A separate mobile layout, bottom navigation, or touch-first flow is not part of the MVP.

Prefer:

- A sidebar for primary navigation at desktop width. Narrow-window behavior is not a delivery requirement.
- Moderate information density. Review screens may show more than entry screens.
- One clear visual hierarchy: place, cycle, then the action being recorded.
- Explicit validation messages next to the field that failed.
- Selectors backed by catalogs, with search.
- The same presentation of dates, times, and units everywhere.
- Controls that can be used without a pointer and that expose labels to assistive technology.

The center of daily production work is the **vidriera detail** view: identity, active cycle, recent operations, and the actions to record work or open history.

The geographic map is how the operator locates a quinta and selects a mapped vidriera. Choosing a polygon opens that same detail view. The map does not replace it and does not become a second place to record operations. Vidrieras that have no polygon stay reachable from the list.

## Current interface

The application shell is a desktop layout with a persistent sidebar, a heading, and a main region. It is sized for a window at least 1280 pixels wide. There is no separate mobile navigation.

Inicio is the only working destination. Later sections are visible in the sidebar and labeled as not available. They do not open a page and they do not show sample operational data.

The interface uses a small set of colors for background, surface, text, borders, and a green accent. These are application chrome, not a brand system. There is still no logo. When a logo or a supplied palette arrives, keep those assets and apply them to the shell. Do not invent a logo to look finished.

User-facing copy stays in Spanish, and `lang="es"` stays on the document. Specifications are in English.

User-facing copy stays in Spanish, matching the current document language and the language of the operation. Specifications are in English and describe behavior, not final microcopy.

## Interaction rules that apply across features

- Creating a related catalog entry (a product, a variety, a person, a quality class) happens without discarding the form the user already started.
- Search existing catalog entries before offering creation.
- Show a possible duplicate before saving a new catalog name.
- A shared operation is entered once. Each affected vidriera links to that same record.
- Dates and times are displayed in the business locale. Store them with a time zone. The working zone for display is `America/Argentina/Buenos_Aires`.
- Units are chosen from the unit catalog. The form shows the dimension so incompatible units are not offered.
- Empty states explain what is missing and which action creates the first record.
- Destructive corrections of historical records are explicit. The product does not silently overwrite a finalized cycle, a closed medianero assignment, or a recorded operation.

## Stage 1 navigation

The first shell only needs destinations that the implemented features use. A reasonable set, added as features land, is:

- Farms and vidrieras, including the quinta map once PROD-06 is present
- The open vidriera
- People
- Crops and varieties
- Products
- Units, available to the people maintaining catalogs

Harvest, inventory, and commercial destinations appear with their stages. Do not add empty modules for uncommitted future work.
