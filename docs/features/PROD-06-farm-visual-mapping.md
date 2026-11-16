# PROD-06 — Farm Visual Mapping

## Metadata
- ID: PROD-06
- Name: Farm Visual Mapping
- Module: Production
- Stage: 1
- Status: Planned
- Priority: P0
- Domains: `FRONTEND` `BACKEND` `DATABASE`
- Dependencies: CORE-01, PROD-01

## Objective

Let the operator locate a quinta and its vidrieras on a geographic map with satellite or aerial imagery, and store an approximate boundary for each mapped record.

## Business Value

Villa Elisa and Arturo Seguí are recognized on the ground by roads, buildings, and the layout of the greenhouses. A map makes that recognition available at the desk. The map is a way to find a production unit. The vidriera detail remains the place where work is recorded.

## Functional Description

The map is part of the desktop application. The basemap comes from an external satellite or aerial imagery provider. The operator does not upload a base image. The imagery only needs to be clear enough to recognize terrain, roads, buildings, and surroundings. It does not need to be recent or survey-grade.

Polygons are geographic coordinates in GeoJSON, using longitude and latitude as in RFC 7946 and WGS84. They are not pixel positions on a particular provider's image. Replacing the imagery provider must not require redrawing saved boundaries.

The Production module owns the geometry. A boundary is an optional attribute or associated record of an existing quinta or vidriera. Drawing a polygon does not create a second physical entity. Canteros have no geometry in this feature.

A preferred client approach, to be confirmed when implementation starts, is Leaflet for the map, an external satellite tile API for the imagery, and Leaflet-Geoman or an equivalent tool for drawing and editing polygons. The API and database remain the existing FastAPI application and PostgreSQL. The first release does not require PostGIS. Validated GeoJSON can be stored with the PostgreSQL already in the architecture. PostGIS is a later option only if spatial queries, indexes, or stricter geometry checks justify it. It is not a new infrastructure service.

The imagery provider is not chosen in this specification. [OQ-29](../OPEN_QUESTIONS.md#oq-29) must be answered before provider-specific code is written. Candidates to compare include MapTiler, Mapbox, Google Maps where its current APIs and terms fit this use, and other legitimate satellite or aerial tile services. Standard OpenStreetMap tiles are not satellite imagery. A Google Earth screenshot is not a basemap license. Deprecated APIs are not candidates. Geographic data stays vendor-neutral either way.

## Expected Behavior

### Quinta boundary

1. The operator starts creating a quinta and enters the administrative information defined by PROD-01.
2. The flow opens an interactive map.
3. The operator searches for a place or pans and zooms until the property is recognizable.
4. The operator activates polygon drawing and clicks the approximate boundary.
5. The operator can edit the polygon before confirming it.
6. Saving persists the quinta and, when a polygon was confirmed, its boundary.

The administrative record can be saved when the mapping step is skipped or the imagery fails to load. A quinta without a boundary is valid. The creation flow still offers mapping before that save so the usual path includes the boundary.

The boundary can be edited later. Editing it does not change the technical identifier or the operational code.

### Vidriera boundary

Once a quinta has a boundary:

1. The operator opens that quinta's map.
2. The map shows the quinta polygon and frames the view on it.
3. The operator draws a polygon for a vidriera.
4. The polygon is attached either to a new vidriera or to an existing vidriera of that quinta that has no polygon yet.
5. The vidriera's operational code is visible on the polygon or in the selection detail.
6. Saving persists the geometry on that vidriera.

The operator can repeat this for other vidrieras in the same quinta. Creating a vidriera from the map uses the same identity rules as PROD-01, including the suggested operational code. Cancelling the draw creates nothing. Attaching a polygon to an existing vidriera does not insert another vidriera.

### Navigation

On a quinta map the operator sees the quinta boundary, every mapped vidriera, and enough labeling or selection detail to read the operational code. Clicking a polygon selects and highlights it and offers the vidriera detail. Vidrieras without geometry remain in the ordinary list and search. They are not hidden because they lack a shape.

Later features may add cycle, operation, harvest, or status overlays. Those overlays are not part of PROD-06. The map does not become a second copy of business records.

## Business Rules

- Each mapped vidriera belongs to exactly one quinta, the same quinta that owns the vidriera record.
- The quinta boundary is the visual working area for drawing its vidrieras. Vidriera polygons are not drawn until that boundary exists.
- A quinta boundary and a vidriera boundary are different geometries.
- A polygon is one GeoJSON Polygon with a single exterior ring. The ring closes, uses longitude then latitude, and has at least four positions (three distinct vertices plus the closing position).
- Self-intersections and rings with too few vertices are invalid. The save is rejected and the previous geometry, if any, is left unchanged. The message tells the operator what to correct.
- The product does not silently move, clip, or simplify a polygon to force it inside the quinta.
- A vidriera polygon that does not intersect its quinta boundary at all is rejected. That relationship is inconsistent, not an approximation.
- A polygon that overlaps another vidriera, or that extends slightly outside the quinta, is stored as drawn and shown with a warning. Whether that warning should become a hard rejection is [OQ-30](../OPEN_QUESTIONS.md#oq-30). Until then the geometry is not rewritten and the warning is visible.
- Greenhouses need not be aligned, and properties need not be rectangles. Containment is approximate. Cadastral accuracy is not required.
- Geometry edits do not change technical identifiers or operational codes.
- Computed polygon area is an approximate footprint. It is not the measured physical area and it is not the productive or cultivated area. This feature does not copy a computed area into measured-area or yield fields.
- Imagery tiles are requested from the provider when the map is open. They are not downloaded into the application database for the MVP. Saved polygons remain if the tiles fail or the provider changes.
- Remembering map center and zoom is optional and is never a substitute for the polygon.
- Provider attribution required by the license is visible on the map. An unrestricted provider secret is not placed in the browser bundle. The concrete authentication method is part of [OQ-29](../OPEN_QUESTIONS.md#oq-29).
- The map requires a network connection to load imagery. Lack of imagery does not delete stored records.

## Data Requirements

| Fact | Required |
| --- | --- |
| Quinta geographic boundary, as a GeoJSON Polygon in WGS84 | No |
| Vidriera geographic boundary, as a GeoJSON Polygon in WGS84 | No |
| The quinta or vidriera the boundary belongs to | Yes, when a boundary exists |
| Provider name, tile URL, or other basemap configuration | No, not stored as domain data |

One quinta has at most one boundary. One vidriera has at most one boundary. Removing a boundary clears the geometry and leaves the production record in place. Deactivating a quinta or vidriera keeps its geometry with the record.

This table is not a SQL column plan. An implementation may store the geometry as an attribute or as an associated record owned by Production.

## User Interactions

- From quinta creation, open the map, search or pan, draw, edit, and save.
- From an existing quinta, add or replace its boundary.
- From a mapped quinta, draw a vidriera polygon and attach it to a new or existing vidriera.
- Select a polygon and open the vidriera detail.
- Use the quinta's vidriera list to open a vidriera that has no polygon.
- See a warning when a saved shape overlaps another vidriera or crosses the quinta edge, without losing the shape that was drawn.
- See an actionable error when the shape is invalid, and keep the prior saved shape.

## Acceptance Criteria

- [ ] The user can open a satellite or aerial map supplied by an external provider.
- [ ] The user can search for or manually navigate to a quinta's geographic location.
- [ ] The user can manually draw a quinta boundary.
- [ ] The user can edit and persist that boundary.
- [ ] The user can draw a vidriera polygon within the quinta.
- [ ] A polygon is associated with exactly one existing vidriera.
- [ ] New vidrieras may be created through the map without creating duplicate records.
- [ ] Vidriera codes are visible in the mapping interface.
- [ ] Selecting a vidriera on the map opens or links to its detail.
- [ ] Existing vidrieras without geometry remain accessible.
- [ ] Invalid polygon geometry is rejected with actionable feedback.
- [ ] The application distinguishes approximate geometry from verified production area.
- [ ] Geometries survive application restarts.
- [ ] Geographic coordinates remain independent of the basemap provider.
- [ ] An imagery loading failure does not delete or corrupt saved geometries.
- [ ] All mapping interactions work at the supported desktop viewport.
- [ ] The interface respects provider attribution and applicable licensing requirements.

## Edge Cases & Validation

- Imagery unavailable, a failed search, or a denied tile request leaves the form and any stored polygons intact and explains that the basemap did not load.
- Saving a quinta with the mapping step incomplete creates the administrative record and no boundary.
- Drawing a vidriera on a quinta that has no boundary is refused, with a path to map the quinta first. The vidriera can still be created from the PROD-01 list.
- A polygon that does not intersect the parent quinta is rejected and not stored.
- Overlap and slight overflow warn and store the drawn coordinates. They do not clip the ring.
- Two draws cannot attach two polygons to the same vidriera. The second save replaces the geometry only through an explicit edit, or is rejected if the operator chose "attach to unmapped" and the vidriera already has a boundary.
- Closing the editor without confirming does not insert a vidriera and does not replace a stored polygon.
- A self-intersecting ring or a ring with fewer than three distinct vertices is rejected.
- Coordinates outside the longitude and latitude ranges of WGS84 are rejected.
- The client does not send pixel offsets as if they were coordinates.

## Out of Scope

- Advanced GIS.
- Cadastral surveying.
- High-precision geographic measurement.
- Automated vidriera detection from imagery.
- Satellite image analysis.
- Crop health indices.
- Remote sensing analytics.
- Drawing individual canteros.
- Automatic productive-area calculations.
- Historical satellite imagery analysis.
- Dynamic agricultural overlays.
- Offline map caching.
- Native mobile mapping.
- Geospatial time-series data.
- IoT sensor mapping.
- Choosing the commercial imagery vendor. That comparison is [OQ-29](../OPEN_QUESTIONS.md#oq-29).
- PostGIS, unless a later review shows that ordinary PostgreSQL is not enough.

## Dependencies & Integration Points

- CORE-01 for the desktop shell. The map is a destination inside that shell, at a width of at least 1280 pixels.
- PROD-01 for quintas, vidrieras, technical identifiers, and operational codes. This feature does not redefine those rules.
- PROD-03, OPS-01, and TRACE-01 do not depend on the map. The vidriera detail remains their entry for recording work.
- The browser loads tiles from the provider selected in [OQ-29](../OPEN_QUESTIONS.md#oq-29). The API persists domain records and GeoJSON only.
- Domain model: [PRODUCTION_MODEL.md](../domain/PRODUCTION_MODEL.md). Conceptual ownership: [DATA_MODEL.md](../architecture/DATA_MODEL.md).

## Open Questions

- [OQ-29](../OPEN_QUESTIONS.md#oq-29) blocks the provider-specific imagery client. It does not block the identity or geometry rules above.
- [OQ-30](../OPEN_QUESTIONS.md#oq-30) asks whether overlap and slight overflow should stay warnings or become rejections. The safe behavior until then is to warn and store the drawn polygon.
