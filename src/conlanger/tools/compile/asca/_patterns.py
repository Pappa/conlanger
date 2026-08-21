"""Shared regex fragments for ASCA compile transforms."""

from __future__ import annotations

import re

_IPA_MODIFIER = r"[\u02B0-\u02B8\u02BC\u02D1\u02E4\u0300-\u036F]"
IPA_SEGMENT = (
    r"[a-zA-Z\u00C0-\u024F\u0250-\u02AF\u1D00-\u1DBF\u0370-\u03FF]+"
    rf"(?:{_IPA_MODIFIER})*"
)

ASCA_ENV_OPTIONAL_RE = re.compile(r"^\([A-Z$%#][A-Z$%#0-9,.…]*\)$")
SET_BODY_RE = re.compile(r"\{([^{}]*)\}")
