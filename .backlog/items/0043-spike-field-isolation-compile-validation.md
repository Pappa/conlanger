Type: spike
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Field-isolation compile validation (go-with-limits).
Result: [0043-field-isolation-compile-validation.md](../spikes/0043-field-isolation-compile-validation.md)
Blocked by:

## Question

Can we raise confidence in **compile validation** by validating **individual index-rule fields** (`input`, `output`, `env`, `exception`) against ASCA when the other fields are replaced by known-valid stubs — without reviving [Rule-derived probe synthesis](10-rule-derived-probe-synthesis.md) (wontfix)?

## Answer

**go-with-limits.** Field isolation with canned stubs + existing `validate_asca` / baseline wordlist can attribute most Tier 1–2 syntax failures to a field; it must not replace whole-rule `ok`, and cross-field cases (sets, condensed balance, insertion+env, deletion-vs-lexicon) will disagree. Stay inside ticket 10: no probe synthesis — only fixed/shape-aware stubs. Record as a fails-only sidecar CSV with a derived `blame` column.

Findings: [research/field-isolation-compile-validation.md](../spikes/field-isolation-compile-validation.md).
