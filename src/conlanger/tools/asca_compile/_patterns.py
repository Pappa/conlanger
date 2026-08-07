"""Shared regex fragments for ASCA compile transforms."""

_IPA_MODIFIER = r"[\u02B0-\u02B8\u02BC\u02D1\u02E4\u0300-\u036F]"
IPA_SEGMENT = (
    r"[a-zA-Z\u00C0-\u024F\u0250-\u02AF\u1D00-\u1DBF]+"
    rf"(?:{_IPA_MODIFIER})*"
)
