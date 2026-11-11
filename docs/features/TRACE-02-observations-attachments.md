# TRACE-02 — Observations & Attachments

## Metadata
- ID: TRACE-02
- Module: Operations
- Stage: 1
- Status: Planned
- Priority: P1
- Domains: `FRONTEND` `BACKEND` `DATABASE` `STORAGE`
- Dependencies: OPS-01

## Objective

Attach photographs to operations, especially observations, so conditions can be reviewed with the history.

## Business Value

A sentence often fails to capture disease pressure, coverage, or a bed's state. A photograph tied to the operation keeps that evidence with the vidriera.

## Functional Description

On an operation, the user attaches one or more image files and an optional caption. The file is stored outside the operation row, and the operation stores the link. The history entry shows that attachments exist and opens them.

Observations are the primary use. Any operation type may receive an attachment, so a heating note or an application can carry a photo too. An observation still requires its description from OPS-02 when that feature is present. This feature can attach a file to an OPS-01 observation that has only notes, until OPS-02 is in place.

Attachments are not analyzed. A file does not create an operation by itself.

## Expected Behavior

- Uploading a JPEG or PNG on an operation shows it on that operation and in history.
- A caption is optional.
- Removing an attachment deletes the link and the stored file, and leaves the operation.
- A non-image upload is rejected.
- Opening an attachment requires an authenticated user.

## Business Rules

- Observations describe conditions and are not assumed to be interventions. See [ADR 0007](../decisions/0007-observations-as-operations.md).
- The file belongs to the operation, not to a parallel observation log.
- Shared operations show the same attachments on every targeted vidriera.

## Data Requirements

| Fact | Required |
| --- | --- |
| Operation | Yes |
| Stored file and content type | Yes |
| Original filename | Yes |
| Caption | No |
| Uploading user | Yes |
| Uploaded-at timestamp | Yes |

## User Interactions

- From an operation, add a photo, optionally caption it, and save.
- View the photo from the operation and from history.
- Remove a photo.

## Acceptance Criteria

- [ ] An authenticated user can attach a PNG or JPEG to an operation and open it afterward.
- [ ] The vidriera history for that operation indicates that an attachment exists.
- [ ] A captionless attachment is accepted.
- [ ] A non-image file is rejected and no attachment record is kept.
- [ ] Removing an attachment leaves the operation and its other attachments in place.
- [ ] A signed-out user cannot retrieve the file.
- [ ] An operation of type observation can carry an attachment without being converted into another type.

## Edge Cases & Validation

- An empty file is rejected.
- A very large upload is rejected with a visible error. The size cap is a technical limit chosen during implementation and stated in the error; it is not a business rule about photograph quality.
- Deleting an operation is rejected while attachments exist, consistent with the rule that referenced history is deactivated or corrected rather than silently removed. The user removes attachments first if an operation must be discarded, or the operation is corrected in place.

## Out of Scope

- Image recognition, automatic tagging, and diagnosis.
- Video and documents.
- A farm-wide photo gallery detached from operations.
- Sensor images.

## Dependencies & Integration Points

- OPS-01 operations are the parent. OPS-02 observation text is shown together with the photo when both exist.
- Storage is introduced here, behind the API, with metadata in PostgreSQL. See [OVERVIEW.md](../architecture/OVERVIEW.md).
- TRACE-01 links to the attachments.

## Open Questions

None.
