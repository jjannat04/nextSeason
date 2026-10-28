"""Explicit, namespaced aliases; never fuzzy match cultivar names."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SLICE = ("aman_rice", "maize", "sunflower", "mung_bean")


class MappingError(ValueError):
    pass


def load_crosswalk(path=None):
    path = path or ROOT / "data/crosswalk/crops.json"
    return json.loads(Path(path).read_text(encoding="utf-8"))


def resolve(raw: str, namespace: str, crosswalk=None):
    aliases = (crosswalk or load_crosswalk())["aliases"]
    matches = [a for a in aliases if a["namespace"] == namespace and a["raw"] == raw]
    if len(matches) != 1 or matches[0].get("status") != "mapped":
        raise MappingError(f"Unresolved or ambiguous crop {raw!r} in {namespace}")
    return matches[0]


def canonical_input(raw):
    if raw not in SLICE:
        raise MappingError(f"Crop is not enabled in the four-crop slice: {raw!r}")
    return raw
