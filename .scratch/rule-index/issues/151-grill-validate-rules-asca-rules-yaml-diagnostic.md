Type: grilling
Status: needs-grilling
Blocked by: 148

# Grill: `validate_rules` compile diagnostic `diagnostics/compile/asca_rules.yml`

Spawned from wayfinder session 2026-10-17. Owner input: after validation, emit a **debug/monitoring** artifact with compiled ASCA syntax per rule (not a new SoT).

## Question

Specify the **`diagnostics/compile/asca_rules.yml`** contract: path, lifecycle (always on `validate_rules` vs flag), ordering, and per-rule payload when compile yields alternatives, skipped rules, or partial field blame.

## Proposed shape (owner draft — lock or amend)

```yaml
sections:
- section: Afro-Asiatic
  index: 6
  rules:
  - rule_id: Proto-Omotic-dz-ʃ-tʃ
    rule: dz ʃ tʃ > ʒ F F
```

Clarify:

- **`rule` string** — full `SoundChangeRule.__str__()` / `.rsca` line, per-stage lines for multi-stage index rules, or one row per compile-expanded pair?
- **`index`** — section number from parsed YAML (type, stability across regen).
- **Skipped** (`status: skipped`) and **section skipped** — omit, include with sentinel, or separate file?
- **Failed compile** — omit rule, include last good string, or error stub?
- **Relation to** `diagnostics/inventory/` CSVs and [103 split](103-split-create-index-and-validate-rules.md) (parse diagnostics under `diagnostics/parse/` only today).

## Depends on

[148](148-grill-asca-shaped-syntax-in-applier-neutral-sot.md) — diagnostic strings are **ASCA compile output**; grill confirms that is the intended reader audience.

## Deliverable

Locked YAML schema + operator doc blurb; implementation can be a follow-on **task** ticket.
