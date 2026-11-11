# Feature specification template

Copy this structure for every committed feature. Keep the specification functional. Implementation tasks such as "add a table" or "add a route" belong in the pull request, not in their own feature.

```markdown
# FEATURE-ID — Feature Name

## Metadata
- ID:
- Module:
- Stage:
- Status:
- Priority:
- Domains:
- Dependencies:

## Objective

## Business Value

## Functional Description

## Expected Behavior

## Business Rules

## Data Requirements

## User Interactions

## Acceptance Criteria

## Edge Cases & Validation

## Out of Scope

## Dependencies & Integration Points

## Open Questions
```

## Metadata rules

- `Status` is `Planned`, `In Progress`, `Implemented`, or `Deferred`.
- `Priority` is `P0`, `P1`, `P2`, or `P3`, as defined in [FEATURES.md](../../FEATURES.md).
- `Domains` uses only the tags that apply: `FRONTEND`, `BACKEND`, `DATABASE`, `STORAGE`, `INFRA`, `ANALYTICS`, `INTEGRATION`.
- `Dependencies` lists feature IDs. Use `None` when there are none.

## Acceptance criteria

Write Markdown checkboxes. Each criterion is observable and testable. Include important rejections and failure cases.

Name the business outcome. "The API exists" and "the UI is intuitive" are not acceptance criteria.

## Data requirements

List the business facts the feature must store or read. Mark each as required or optional. Do not prescribe column names or SQL types unless a constraint would be ambiguous without them.

Put uncertain rules under Open Questions instead of turning them into required fields.

## Links

Link domain documents, decision records, and open questions with relative paths. When an open question is resolved, update this specification in the same change.
