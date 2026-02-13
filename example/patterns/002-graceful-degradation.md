---
number: 2
name: Graceful Degradation
confidence: 2
contains: [13]
contained_by: []
tags: [resilience, reliability, architecture]
---

Systems that treat every dependency as equally critical will fail completely when any single dependency becomes unavailable, even if the core functionality could continue without it.

## Discussion

A modern system depends on many services: databases, caches, external APIs, message queues. Not all of these are equally essential to every request. A product page can still render without personalized recommendations. A checkout can still proceed without real-time analytics.

Yet the default behavior of most systems is total failure. If the recommendation service is down, the entire page returns a 500. This is because error handling is often an afterthought — the "happy path" is built first, and failure modes are never explicitly designed.

Graceful degradation requires *intentional* design. You must decide, for each dependency, what happens when it is unavailable. This decision is an architectural choice, not an implementation detail.

## Solution

Classify every external dependency by its criticality to each user-facing operation. For non-critical dependencies, define a fallback: cached data, a sensible default, or simply omitting the feature. Implement circuit breakers to prevent cascading failures. Make the degraded state visible to operators but invisible (or at least acceptable) to users.
