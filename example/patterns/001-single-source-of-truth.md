---
number: 1
name: Single Source of Truth
confidence: 2
contains: [11, 12]
contained_by: []
tags: [data, consistency, architecture]
---

When the same piece of knowledge is defined in multiple places, changes to one copy inevitably fall out of sync with the others, leading to subtle bugs and eroded trust in the system.

## Discussion

Every piece of knowledge in a system should have a single, authoritative representation. This is one of the most fundamental principles in software architecture, yet one of the most frequently violated.

Duplication arises naturally: a database schema is mirrored in an ORM model, which is mirrored in an API response type, which is mirrored in a frontend type. Each copy is a liability. When the source changes, every copy must change in lockstep — and they rarely do.

The cost of duplication is not just the effort of keeping copies in sync. It is the *uncertainty* about which copy is authoritative. When developers encounter conflicting information, they lose confidence in the system.

## Solution

For every piece of knowledge, designate exactly one authoritative source. Derive all other representations from it automatically — through code generation, schema inference, or runtime derivation. If two components need the same data shape, one should import it from the other rather than redefining it.
