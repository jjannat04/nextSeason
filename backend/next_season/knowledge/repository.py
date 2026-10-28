"""Read the reviewed projection only; never load raw CSVs in a request."""
import json
from pathlib import Path
from .identity import ROOT, SLICE


class DatasetSafetyError(ValueError):
    pass


def load_dataset(mode="production", *, allow_fixtures=False, path=None):
    if mode not in ("production","prototype_recommendation","development_fixture"):
        raise DatasetSafetyError("Unknown dataset mode")
    if mode=="development_fixture":
        if not allow_fixtures:
            raise DatasetSafetyError("Development fixtures are disabled on this server")
        path=path or ROOT/"tests/fixtures/development_knowledge.json"
    else:
        path=path or ROOT/"data/normalized"/("prototype_slice.json" if mode=="prototype_recommendation" else "slice.json")
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    text=json.dumps(data)
    if mode!="development_fixture" and (data.get("origin")!="RESEARCH_EVIDENCE" or "DEVELOPMENT_FIXTURE" in text):
        raise DatasetSafetyError("Fixture/untrusted dataset cannot enter production")
    if mode=="development_fixture" and data.get("origin")!="DEVELOPMENT_FIXTURE":
        raise DatasetSafetyError("Fixture mode requires the isolated fixture dataset")
    if set(c["id"] for c in data["crops"])!=set(SLICE):
        raise DatasetSafetyError("Dataset must contain exactly the four slice crops")
    if mode=="prototype_recommendation":
        from .prototype import fingerprint,INPUTS
        if data.get("release_mode")!=mode or set(data.get("release_inputs",{}))!=set(INPUTS):
            raise DatasetSafetyError("Prototype release metadata missing")
        if any(fingerprint(ROOT/"data/normalized"/name)!=sha for name,sha in data["release_inputs"].items()):
            raise DatasetSafetyError("Prototype sources changed; rebuild and review the offline projection")
    return data


def usable(field, use):
    states=("verified","provisional") if use=="prototype_recommendation" else ("verified",)
    return bool(field and field.get("verification") in states and use in field.get("allowed_uses",[])
                and field.get("normalized_value") is not None)
