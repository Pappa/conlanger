Type: task
Status: needs-detail
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Policy for inventory `no composed chain paths from stages` failures.
Blocked by:

## Problem Statement

Multi-stage rules fail inventory when no composed chain path matches: each step’s compiled input must equal the previous step’s compiled output. At least three corpus rules hit this after composed-chain enumeration (split vs merged stage I/O, stress materialization mismatches).

## Description

Decide inventory policy: strict per-step equality vs allowed merged sets, and whether fixes belong in code, SoT edits, or documented hold-outs (`status: skipped` / comments per historical-fidelity policy).

## Acceptance Criteria

- [ ] **Answer** classifies affected rules as fixable vs permanent hold-out with rationale.
- [ ] Policy covers how composed chain paths interact with inventory and compiled YAML validation.
- [ ] **`Status: resolved`** with **Answer** per implement-closure.

## Comments
