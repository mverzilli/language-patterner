---
number: 22
name: Parse Don't Validate
confidence: 1
contains: []
contained_by: [12]
tags: [types, safety, code]
---

When validation checks are separate from data transformation, the knowledge that "this data is valid" exists only as a runtime convention that the type system cannot enforce, leading to redundant checks and missed edge cases.

## Discussion

Traditional validation works like a bouncer at a club: it checks your ID and lets you in, but once you are inside, nobody remembers that you were checked. Functions deeper in the call stack must either re-validate (wasteful) or trust that validation happened upstream (fragile).

Parsing is a stronger operation. Instead of checking that data satisfies constraints and returning a boolean, it transforms unstructured data into a structured type that *encodes* the constraints. Once you have a `NonEmptyList`, you know it is non-empty — not because someone checked, but because the type makes it impossible to construct an empty one.

This principle, articulated by Alexis King, bridges the gap between dynamic validation and static type safety. It pushes the boundary of "trusted" data as far outward as possible.

## Solution

At system boundaries, parse incoming data into types that encode your invariants. Instead of `validate(data) -> bool`, write `parse(data) -> ValidatedType | Error`. Use the type system to make invalid states unrepresentable. Functions that accept `ValidatedType` never need to re-check the invariants — the type guarantees them.
