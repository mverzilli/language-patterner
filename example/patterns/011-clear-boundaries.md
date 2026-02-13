---
number: 11
name: Clear Boundaries
confidence: 2
contains: [21]
contained_by: [1]
tags: [modularity, encapsulation, components]
---

When modules expose their internal data structures and implementation details, every consumer becomes tightly coupled to those details, making changes expensive and risky.

## Discussion

A module's boundary is the contract it offers to the outside world. When this boundary is blurry — when internal types leak out, when consumers reach into private state, when implementation details appear in public interfaces — the module cannot evolve independently.

Good boundaries are like cell membranes: they allow controlled exchange while protecting the interior. The public interface should express *what* the module does, not *how* it does it.

This pattern works at every scale: function signatures, class APIs, module exports, service contracts. The principle is the same — minimize the surface area that consumers depend on.

## Solution

Define explicit public interfaces for every module. Hide all internal state and types behind these interfaces. Use the language's access control mechanisms (private fields, unexported symbols, internal packages) to enforce the boundary. When a consumer needs something that is currently internal, consider whether the interface should grow — or whether the consumer's design should change.
