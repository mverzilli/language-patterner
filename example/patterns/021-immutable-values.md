---
number: 21
name: Immutable Values
confidence: 2
contains: []
contained_by: [11]
tags: [data, safety, code]
---

When data structures can be modified by any code that holds a reference to them, tracking down where and when a value changed becomes a debugging nightmare, especially in concurrent systems.

## Discussion

Mutable shared state is the root cause of a large class of bugs. When a function receives an object, modifies it, and returns — the caller's copy has changed too. When two threads access the same data structure, the result depends on timing. When a cache holds a reference to a mutable object, any code can silently corrupt the cache.

Immutable values eliminate these problems entirely. If a value cannot change after creation, sharing it is always safe. There are no race conditions, no spooky action at a distance, no defensive copying.

The performance concern is usually overstated. Modern runtimes optimize immutable data aggressively, and structural sharing (as in persistent data structures) makes "copying" nearly free.

## Solution

Prefer immutable data structures for values that are shared across boundaries (function calls, module boundaries, threads). Use the language's immutability features (frozen dataclasses, `const`, `readonly`, records). When mutation is necessary for performance, confine it to a small scope and expose only immutable views to the outside.
