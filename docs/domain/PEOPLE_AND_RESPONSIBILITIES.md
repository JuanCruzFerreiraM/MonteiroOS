# People and responsibilities

## Confirmed

The system distinguishes these relationships:

| Relationship | Meaning |
| --- | --- |
| Medianero | Production partner responsible for assigned areas. Not an ordinary employee. Financial terms are unknown. |
| Employee | Staff who perform work for the business. |
| Operation performer | A person who carries out a particular operation. There may be several, or none. |
| Responsible person | A person accountable for a particular operation. May differ from the performer. |
| Recording person | The business person who entered the information, when that person is known. Not a software account. |

One person may hold more than one relationship. The person who records an operation may differ from the person who performs it.

A vidriera is either assigned to one medianero or managed directly by Monteiro. Direct management is an explicit state. It does not create a fictitious medianero. Assignments and direct-management intervals keep their history, including a start and, when the interval ends, an end. Changing responsibility must not overwrite the previous interval. Records from that interval stay attributable to it.

Monteiro generally purchases agricultural inputs and other production materials. That purchasing habit does not decide who bears the cost. Purchaser, physical consumer, and economic responsibility stay separate. Cost-sharing rules with medianeros are unresolved.

Not every activity has a human executor.

## Working assumptions

- A person is a durable record with a name. Contact details are optional. Real people are entered by the business and are not seeded.
- Roles are attributes of a person over a validity interval. They are not separate person records.
- The MVP has one software operator and no per-person accounts. See [ADR 0009](../decisions/0009-single-user-desktop-first.md).
- A vidriera has at most one open responsibility interval: one medianero, or direct management. [OQ-22](../OPEN_QUESTIONS.md#oq-22) is resolved.
- The medianero assignment belongs to the vidriera, not to a cultivation cycle. Cycles that fall inside an assignment interval can be reported later without copying the assignment onto each cycle.
- Deactivating a person hides them from new selections and keeps existing operations and assignments readable.

## Unknowns

- Which facts the business already keeps about each medianero ([OQ-12](../OPEN_QUESTIONS.md#oq-12)).
- Monteiro generally purchases inputs. Who bears the cost on a medianero vidriera is still open ([OQ-13](../OPEN_QUESTIONS.md#oq-13), [OQ-14](../OPEN_QUESTIONS.md#oq-14)).
- How costs are shared ([OQ-14](../OPEN_QUESTIONS.md#oq-14)).
- Who sits at the desktop during the pilot is an operational detail. The product decision is already single-user and desktop-first ([OQ-20](../OPEN_QUESTIONS.md#oq-20)).

No screen or calculation may assume a cost split, a wage, or a settlement formula for a medianero.

## Implications for the software

- Store people, role intervals, and vidriera assignments separately.
- Close an assignment by setting an end, not by editing it into the new person.
- Store operation participants as links to people, with a participant kind of performer or responsible.
- Store an optional recording person on the operation even when no performer is set. Do not store a software account.
