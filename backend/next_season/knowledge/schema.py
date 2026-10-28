"""Field-level evidence contracts. Missing is never a numeric value."""
from enum import StrEnum
from typing import Any, TypedDict


class Verification(StrEnum):
    VERIFIED = "verified"
    PROVISIONAL = "provisional"
    CONFLICTING = "conflicting"
    MISSING = "missing"
    NOT_APPLICABLE = "not_applicable"


class EvidenceField(TypedDict):
    raw_value: str
    normalized_value: Any
    verification: str
    source: dict
    confidence: str | None
    notes: str | None
    geographic_applicability: str | None
    provenance: dict
    unit: str | None
    allowed_uses: list[str]


MISSING_TOKENS = {"", "n/a", "na", "unknown", "null", "none", "nan", "-"}


def normalize_value(raw: str, kind: str = "text"):
    value = raw.strip()
    if value.lower() in MISSING_TOKENS:
        return None
    if kind == "number":
        from decimal import Decimal, InvalidOperation
        try:
            number = Decimal(value)
            if not number.is_finite():
                raise ValueError("Non-finite scientific value")
            return int(number) if number == number.to_integral() else float(number)
        except InvalidOperation as exc:
            raise ValueError(f"Not a number: {raw!r}") from exc
    if kind == "boolean":
        tokens = {"yes": True, "true": True, "no": False, "false": False}
        if value.lower() not in tokens:
            raise ValueError(f"Not a boolean: {raw!r}")
        return tokens[value.lower()]
    return value
