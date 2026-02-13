---
number: 13
name: Circuit Breaker
confidence: 2
contains: []
contained_by: [2]
tags: [resilience, networking, components]
---

When a dependency is failing, continuing to send it requests wastes resources, increases latency, and can turn a partial outage into a complete one through cascading failures.

## Discussion

Network calls fail. Services go down. Databases become overloaded. When this happens, the natural behavior of a client is to keep trying — and to keep waiting for responses that will never come. Each pending request consumes a thread, a connection, and the patience of an end user.

The circuit breaker pattern, borrowed from electrical engineering, provides a systematic solution. Like its physical counterpart, a software circuit breaker monitors for failures and "trips" when a threshold is reached, immediately rejecting subsequent requests without attempting the call. After a cooling period, it allows a test request through — and if it succeeds, the circuit closes again.

This pattern is particularly important in microservice architectures, where a single failing service can bring down dozens of others through resource exhaustion.

## Solution

Wrap calls to external dependencies in a circuit breaker that tracks failure rates. When failures exceed a threshold within a time window, open the circuit: fail immediately with a known error rather than waiting for timeouts. Periodically allow a single test request to check if the dependency has recovered. Log circuit state changes so operators can track system health.
