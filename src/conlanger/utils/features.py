"""ASCA feature-matrix string helpers shared by compile transforms."""

from __future__ import annotations

import re


def add_features_to_matrix_body(features: str, extra: tuple[str, ...]) -> str:
    """Append signed feature tokens to a matrix body, skipping polarity clashes."""
    body = features
    for feature in extra:
        token = feature if feature.startswith(("+", "-")) else f"+{feature}"
        if token in body or f"-{token.lstrip('+-')}" in body:
            continue
        body = f"{body},{token}" if body else token
    return body


def apply_features_to_token(token: str, extra: tuple[str, ...]) -> str:
    """Merge ``extra`` into ``host:[body]``, or wrap a bare token as ``token:[...]``."""
    if not extra:
        return token
    match = re.fullmatch(r"(.+):\[([^\]]+)\]", token)
    if match:
        host, body = match.group(1), match.group(2)
        return f"{host}:[{add_features_to_matrix_body(body, extra)}]"
    return f"{token}:[{add_features_to_matrix_body('', extra)}]"


def merge_mapping_with_features(mapping: str, features: str) -> str:
    """Apply comma-separated ``features`` to a mapping token or braced set."""
    extra = tuple(part.strip() for part in features.split(",") if part.strip())
    if mapping.startswith("{") and mapping.endswith("}"):
        members = [part.strip() for part in mapping[1:-1].split(",") if part.strip()]
        return (
            "{"
            + ",".join(
                merge_mapping_with_features(member, features) for member in members
            )
            + "}"
        )
    return apply_features_to_token(mapping, extra)
