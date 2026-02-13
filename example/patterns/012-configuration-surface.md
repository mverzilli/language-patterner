---
number: 12
name: Configuration Surface
confidence: 1
contains: [22]
contained_by: [1]
tags: [configuration, flexibility, components]
---

When a component's behavior can only be changed by modifying its source code, adapting it to new contexts requires forking rather than configuring, leading to divergent copies that are hard to maintain.

## Discussion

Every component makes assumptions: default timeout values, retry counts, feature flags, format strings. When these assumptions are buried in the code, the only way to change them is to edit the source. This forces a choice between maintaining a fork or submitting upstream changes for what may be a very specific need.

The opposite extreme is equally harmful: exposing every internal decision as a configuration option creates a bewildering surface area. Users cannot distinguish the important knobs from the trivial ones, and the component becomes harder to understand than the problem it solves.

The right configuration surface is intentional. It exposes the decisions that *legitimately vary* across contexts while keeping everything else as sensible, opinionated defaults.

## Solution

Identify the decisions in your component that will genuinely differ across deployment contexts. Expose these — and only these — as configuration. Use sensible defaults so the component works out of the box. Group related options and document the *intent* behind each one, not just its type.
