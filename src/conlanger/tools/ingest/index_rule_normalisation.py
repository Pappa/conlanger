"""Ordered **index rule normalisation** on the parse working line (ADR-0016).

Concrete transforms land in ticket 143; until then this step is a no-op placeholder
so ``parse_rule_element`` keeps the settled pipeline order.
"""


def apply_index_rule_normalisation(working: str) -> str:
    """Apply lossless or policy-documented surface normalisation after manual mappings."""
    return working
