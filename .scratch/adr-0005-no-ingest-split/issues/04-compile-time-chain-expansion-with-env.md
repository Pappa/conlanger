Type: grilling
Status: resolved
Blocked by: 01

# Corpus shape for chained rules (env / exception)

## Question

~126 chained rules carry `env` and/or `exception`. Does a multi-step chain in HTML imply multiple env/exception fields in the corpus, or the same single-field model as any other rule?

## Answer

**Corpus shape only** — not a separate “propagation strategy” choice.

A series of sound changes on one HTML line is **one corpus rule**: one `input`, one `output` (with ` > ` chain segments), and at most **one** optional `env` and **one** optional `exception`. There are no per-step env/exception fields in YAML.

Compile-time expansion (see [Compile-time chain expansion](03-compile-time-chain-expansion.md)) splits the **output chain** into sequential applier rules; the rule-level `env` and `exception` (when present) apply to **each** emitted ASCA rule. Implementation detail lives in ticket 03, not a second policy fork.
