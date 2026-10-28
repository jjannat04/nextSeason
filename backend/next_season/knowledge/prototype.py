"""Offline, reproducible prototype release. Never consult the raw researcher CSVs."""
import copy
import csv
import hashlib
import json
from .identity import ROOT

ELIGIBLE_STATES = ("verified", "provisional")
INPUTS = ("slice.json", "crop_calendar_verified.csv", "crop_rotation_rules_verified.csv", "rainfall_references_verified.json")
CALENDARS = {"aman_rice": "VCAL01", "maize": "VCAL03", "sunflower": "VCAL04"}


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    base = ROOT / "data/normalized"
    data = copy.deepcopy(json.loads((base / "slice.json").read_text(encoding="utf-8")))
    def read(name):
        with (base / name).open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))
    calendars = read("crop_calendar_verified.csv")
    rainfall = json.loads((base / "rainfall_references_verified.json").read_text(encoding="utf-8"))
    for crop in data["crops"]:
        crop["annual_rainfall"] = rainfall.get(crop["id"], {})
        crop["calendars"] = []
        crop["prototype_eligible"] = False
        crop["prototype_exclusion"] = "No complete calendar aligned with the documented rice/dry-season system; the Kharif-II mungbean calendar cannot substitute for late Rabi."
        for record in calendars:
            if record["calendar_id"] != CALENDARS.get(crop["id"]):
                continue
            state = record["calendar_classification"]
            if state == "production_safe":
                state = "verified"
            if state not in ELIGIBLE_STATES:
                continue
            required = ("planting_start_month", "planting_end_month", "harvest_start_month", "harvest_end_month", "harvest_end_year_offset")
            if not all(record.get(key) for key in required):
                continue
            crop["calendars"].append({"id": record["calendar_id"], "verification": state,
                "allowed_uses": ["prototype_recommendation"], "precision": record["precision"],
                "months": {key: int(record[key]) for key in required}, "record": record,
                "source": {"source_title": record["source_title"], "source_url": record["source_url"], "source_year": record["source_year"], "locator": record["source_locator"]},
                "raw_value": json.loads(record["original_value"]), "normalized_value": json.loads(record["verified_value"]),
                "geographic_applicability": record["region"], "confidence": record["confidence"],
                "notes": "Planting-window evidence is based on a Bangladesh agricultural calendar and may vary by local cultivar and location. Qualifiers remain in the source record; whole-month envelopes are conservative, not exact dates."})
        climate = crop["temperature"]
        soil = crop["soil_ph"]
        fields = [climate.get(k) for k in ("temp_optimal_min_c", "temp_optimal_max_c", "temp_absolute_min_c", "temp_absolute_max_c")] + [soil.get(k) for k in ("soil_ph_opt_min", "soil_ph_opt_max")]
        if crop["calendars"] and all(f and f["verification"] in ELIGIBLE_STATES and f["normalized_value"] is not None for f in fields):
            crop["prototype_eligible"] = True
            crop["prototype_exclusion"] = None
        for field in fields:
            if field and field["verification"] in ELIGIBLE_STATES:
                field["allowed_uses"] = sorted(set(field["allowed_uses"] + ["prototype_recommendation"]))
                field["applicability_status"] = "provisional"
    rules = []
    rule_records = read("crop_rotation_rules_verified.csv")
    for record in rule_records:
        status = record["verification_status"]
        if status not in ("verified_conditional_system_evidence", "provisional_derived_annual_return"):
            continue
        if record["compatibility_class"] == "unresolved":
            continue
        rules.append({"id": record["rule_id"], "previous": record["previous_crop"], "next": record["next_crop"],
            "verification": "provisional", "allowed_uses": ["prototype_recommendation"],
            "evidence_type": "direct_sequence_evidence", "derivation": "reported_forward_system" if status.startswith("verified_") else "inferred_annual_return_not_separate_trial",
            "compatibility_class": record["compatibility_class"], "hard_constraint": False,
            "source": {"source_title": record["source_title"], "source_url": record["source_url"], "source_year": record["source_year"], "locator": record["source_locator"]},
            "raw_value": json.loads(record["original_value"]), "normalized_value": record["compatibility_class"],
            "geographic_applicability": record["bangladesh_applicability"], "confidence": record["confidence"],
            "notes": record["reason"] + " Conditions: " + record["management_conditions"], "record": record})
    data.update(origin="RESEARCH_EVIDENCE", release_mode="prototype_recommendation", schema_version="prototype.1",
        rotation_rules=rules, release_inputs={name: fingerprint(base / name) for name in INPUTS},
        sequence_evidence_coverage=[{"previous": a, "next": b,
            "evidence_type": "direct_sequence_evidence" if any(r["previous"]==a and r["next"]==b for r in rules) else "no_evidence",
            "verification": "provisional" if any(r["previous"]==a and r["next"]==b for r in rules) else "unresolved",
            "ranking_effect": "qualitative_source_class_only" if any(r["previous"]==a and r["next"]==b for r in rules) else "none",
            "hard_constraint": False} for a in (c["id"] for c in data["crops"]) for b in (c["id"] for c in data["crops"])],
        limitations=["Month envelopes retain mid/late/early qualifiers as evidence; they are not exact planting dates.",
            "Candidate search enumerates documented alternating rice/dry-crop systems; unexamined pairs are unknown, not prohibited or penalized.",
            "Sequence evidence comes from coastal Bangladesh; transfer to another locality or cultivar is provisional and management-dependent.",
            "Unknown turnaround is not assumed to be zero: non-overlapping month windows establish temporal order only; field preparation must be checked locally.",
            "Historical temperature comparisons are qualitative reference screening, not yield prediction or a forecast."])
    eligible = {c["id"] for c in data["crops"] if c["prototype_eligible"]}
    for crop in data["crops"]:
        if crop["id"] in eligible and not any(r["previous"] == crop["id"] and r["next"] in eligible or r["next"] == crop["id"] and r["previous"] in eligible for r in rules):
            crop["prototype_eligible"] = False
            crop["prototype_exclusion"] = "No usable sequence evidence connects this crop to the eligible subset."
    if "DEVELOPMENT_FIXTURE" in json.dumps(data):
        raise ValueError("Fixture data cannot enter a prototype release")
    (base / "prototype_slice.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (base / "prototype_crop_subset.csv").open("w", encoding="utf-8", newline="") as handle:
        columns = ["crop_id", "identity", "calendar", "climate_requirements", "basic_soil_requirements", "sequence_evidence", "prototype_recommendation_allowed", "water", "salinity", "stage_stress", "soil_health", "economics", "notes"]
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for crop in data["crops"]:
            writer.writerow({"crop_id": crop["id"], "identity": "verified", "calendar": "provisional" if crop["prototype_eligible"] else "missing",
                "climate_requirements": "verified", "basic_soil_requirements": "verified", "sequence_evidence": "provisional",
                "prototype_recommendation_allowed": str(crop["prototype_eligible"]).lower(),
                **{key: "insufficient_data" for key in ("water", "salinity", "stage_stress", "soil_health", "economics")},
                "notes": crop["prototype_exclusion"] or "Global species applicability and national/calendar versus coastal sequence transfer are provisional, disclosed in results. No cultivar-specific validation claimed."})
    return data


if __name__ == "__main__":
    result = build()
    print("Prototype-eligible:", ", ".join(c["id"] for c in result["crops"] if c["prototype_eligible"]))
