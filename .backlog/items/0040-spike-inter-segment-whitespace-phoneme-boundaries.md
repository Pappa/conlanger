Type: spike
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Inter-segment whitespace and phoneme boundaries (ASCA/Brassica).
Result: [0040-inter-segment-whitespace-phoneme-boundaries.md](../spikes/0040-inter-segment-whitespace-phoneme-boundaries.md)
Blocked by:

## Question

How should Index Diachronica rule fields gain **inter-segment whitespace** so the **applier-neutral** cleaned index matches ASCA and Brassica’s space-separated phoneme convention — including how to detect **digraph / trigraph** graphemes and phoneme boundaries around length markers, feature matrices, class letters, sets, and subscript compounds?

## Answer

**Compile-only for Brassica inter-segment spaces; keep Index-shaped SoT.** ASCA 0.10.2 does **not** require space-separated phonemes (IPA trie + optional whitespace); Brassica does. Index I/O spaces mostly mean **parallel condensed parts**, not phoneme boundaries. Digraph problem for ASCA is **ties** (`t͡ʃ`), not spaces.

Findings: [research/inter-segment-whitespace-phoneme-boundaries.md](../spikes/inter-segment-whitespace-phoneme-boundaries.md) · examples: [research/inter-segment-whitespace-examples.csv](../spikes/inter-segment-whitespace-examples.csv).
