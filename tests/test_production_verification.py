"""Evidence-release invariants; scientific unknowns cannot become active defaults."""
import csv
import hashlib
import json
import unittest

from next_season.knowledge.identity import ROOT, SLICE, resolve
from next_season.knowledge.repository import load_dataset
from next_season.engine.generation import generate


def rows(name):
    with (ROOT / "data/normalized" / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class ProductionVerificationTests(unittest.TestCase):
    def test_evidence_is_anchored_to_unchanged_originals(self):
        manifest = json.loads((ROOT / "data/normalized/production_verification_manifest.json").read_text(encoding="utf-8"))
        for name, expected in manifest["raw_sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT / "research/csv" / name).read_bytes()).hexdigest(), expected)
        with (ROOT / "research/csv/2_crop_calendar.csv").open(encoding="utf-8-sig", newline="") as handle:
            originals = {r["calendar_id"]: r for r in csv.DictReader(handle)}
        for record in rows("crop_calendar_verified.csv"):
            original = originals[record["original_record_id"]]
            self.assertEqual(json.loads(record["original_value"]), original)
            self.assertEqual(resolve(original["crop_id"], "2_crop_calendar.csv")["canonical_id"], record["crop_id"])
        for name, item in manifest["artifacts"].items():
            self.assertEqual(hashlib.sha256((ROOT / "data/normalized" / name).read_bytes()).hexdigest(), item["sha256"])

    def test_month_and_emergence_evidence_never_becomes_exact_days(self):
        for record in rows("crop_calendar_verified.csv"):
            for column in ("planting_start_day", "planting_end_day", "harvest_start_day", "harvest_end_day", "minimum_gap_days"):
                self.assertEqual(record[column], "")
            if record["harvest_after_days_basis"]:
                self.assertIn("days_after_emergence", record["harvest_after_days_basis"])
                self.assertEqual(record["harvest_start_month"], "")
                self.assertEqual(record["harvest_end_month"], "")

    def test_all_pairs_are_explicit_and_unknowns_are_not_neutral(self):
        records = rows("crop_rotation_rules_verified.csv")
        self.assertEqual({(r["previous_crop"], r["next_crop"]) for r in records}, {(a, b) for a in SLICE for b in SLICE})
        for record in records:
            self.assertEqual(record["minimum_gap_days"], "")
            self.assertNotIn("weight", record)
            if record["verification_status"] == "unresolved":
                self.assertEqual(record["compatibility_class"], "unresolved")
                self.assertEqual(record["hard_constraint"], "false")
                self.assertEqual(record["production_activation_allowed"], "false")

    def test_raw_variety_rules_remain_traceable_without_transferring_approval(self):
        with (ROOT / "research/csv/8_crop_rotation_rules.csv").open(encoding="utf-8-sig", newline="") as handle:
            originals = list(csv.DictReader(handle))
        relevant = [r for r in originals if all(resolve(r[k], "8_crop_rotation_rules.csv")["canonical_id"] in SLICE for k in ("previous_crop_id", "next_crop_id"))]
        recorded = {}
        for record in rows("crop_rotation_rules_verified.csv"):
            for original in json.loads(record["original_value"]):
                self.assertIn(original, relevant)
                recorded[original["rule_id"]] = original
        self.assertEqual(recorded, {r["rule_id"]: r for r in relevant})

    def test_reference_verification_does_not_activate_production(self):
        decisions = rows("production_crop_subset.csv")
        self.assertEqual({r["crop_id"] for r in decisions}, set(SLICE))
        for record in decisions:
            self.assertEqual(record["production_recommendation_allowed"], "false")
            self.assertTrue(record["required_blockers"])
            for optional in ("water_supported", "salinity_supported", "stage_sensitivity_supported"):
                self.assertEqual(record[optional], "insufficient_data")
        dataset = load_dataset("production")
        self.assertNotIn("DEVELOPMENT_FIXTURE", json.dumps(dataset))
        candidates, _ = generate(dataset, {"horizon": 2, "priorities": {"preferred_crops": 1}})
        self.assertEqual(candidates, [])


if __name__ == "__main__":
    unittest.main()
