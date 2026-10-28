"""Real agronomic release records; simulated environmental inputs only inside tests."""
import copy
from datetime import date, timedelta
import json
import unittest
from unittest.mock import patch

from test_milestone1 import TestProvider, input_data
from next_season.knowledge.identity import ROOT
from next_season.knowledge.repository import load_dataset, usable, DatasetSafetyError
from next_season.engine.month_generation import generate_months, month_end, month_start
from next_season.engine.prototype_evaluation import confidence, climate
from next_season.engine.service import plan
from django.test import Client


def request_data():
    data = input_data()
    data.update(mode="prototype_recommendation", crop_history=[], horizon=3,
        priorities={"climate_suitability": 1, "preferred_crops": .5})
    data["location"] = {"latitude": 22.8, "longitude": 89.55, "country_code": "BD"}
    data["soil"] = {"ph": 6.1, "ph_method": "water"}
    return data


class PrototypeTests(unittest.TestCase):
    def test_three_real_crops_participate_with_provisional_status(self):
        result = plan(request_data(), TestProvider())
        self.assertEqual(set(result["eligible_crop_ids"]), {"aman_rice", "maize", "sunflower"})
        self.assertTrue(result["is_recommendation"])
        self.assertGreaterEqual(len(result["candidate_rotations"]), 2)
        participating = {a["crop_id"] for c in result["candidate_rotations"] for a in c["activities"]}
        self.assertEqual(participating, set(result["eligible_crop_ids"]))
        self.assertEqual(result["ranking"]["status"], "ranked")
        for candidate in result["candidate_rotations"]:
            self.assertTrue(all(a["calendar_evidence"]["verification"] == "provisional" for a in candidate["activities"]))
            self.assertTrue(any(e["dimension"] == "calendar" and e["verification"] == "provisional" for e in candidate["explanations"]))

    def test_unknown_states_cannot_be_used_for_suitability(self):
        for state in ("unresolved", "missing", "conflicting"):
            field = {"verification": state, "normalized_value": 0, "allowed_uses": ["prototype_recommendation"]}
            self.assertFalse(usable(field, "prototype_recommendation"))
        field["verification"] = "provisional"
        self.assertTrue(usable(field, "prototype_recommendation"))

    def test_unresolved_calendar_excluded_even_if_eligibility_flag_set(self):
        data = copy.deepcopy(load_dataset("prototype_recommendation"))
        for c in data["crops"]:
            for cal in c["calendars"]:
                cal["verification"] = "unresolved"
        self.assertEqual(generate_months(data, request_data())[0], [])

    def test_unresolved_climate_or_soil_never_participates(self):
        for group, key in (("temperature", "temp_optimal_min_c"), ("soil_ph", "soil_ph_opt_min")):
            data = copy.deepcopy(load_dataset("prototype_recommendation"))
            data["crops"][0][group][key]["verification"] = "unresolved"
            self.assertEqual(generate_months(data, request_data())[0], [])

    def test_unresolved_rule_is_not_a_weight_or_constraint(self):
        data = copy.deepcopy(load_dataset("prototype_recommendation"))
        for rule in data["rotation_rules"]:
            rule["verification"] = "unresolved"
        self.assertEqual(generate_months(data, request_data())[0], [])
        self.assertFalse(any(r["hard_constraint"] for r in data["rotation_rules"]))

    def test_month_envelopes_do_not_overlap_and_gaps_are_visible(self):
        result = plan(request_data(), TestProvider())
        for candidate in result["candidate_rotations"]:
            for activity in candidate["activities"]:
                self.assertEqual(len(activity["planting_window"]["start"]), 7)
                self.assertIn("idle_before", activity)
                self.assertNotIn("turnaround_days", activity)
            for previous, next_ in zip(candidate["activities"], candidate["activities"][1:]):
                self.assertLess(month_end(previous["harvest_window"]["end"]), month_start(next_["planting_window"]["start"]))

    def test_constraints_and_deadline_use_latest_possible_harvest(self):
        data = request_data()
        data["constraints"] = {"required_crop_ids": ["sunflower"], "excluded_crop_ids": ["maize"], "locked_slots": {"0": "sunflower"}, "earliest_planting": "2027-01-01"}
        result = plan(data, TestProvider())
        self.assertTrue(result["candidate_rotations"])
        for c in result["candidate_rotations"]:
            self.assertTrue(all(a["crop_id"] != "maize" for a in c["activities"]))
            self.assertEqual(c["activities"][0]["crop_id"], "sunflower")
            self.assertTrue(all(check["status"] == "satisfied" for check in c["hard_constraints"]))
        data["constraints"]["latest_harvest"] = "2027-01-02"
        self.assertEqual(plan(data, TestProvider())["candidate_rotations"], [])

    def test_current_field_occupancy_respected(self):
        data = request_data()
        data["current_crop"] = {"crop_id": "aman_rice", "harvest_date": "2027-01-10"}
        result = plan(data, TestProvider())
        self.assertTrue(result["candidate_rotations"])
        self.assertTrue(all(month_start(c["activities"][0]["planting_window"]["start"]) > date(2027, 1, 10) for c in result["candidate_rotations"]))

    def test_optional_gaps_are_not_zero_or_a_release_block(self):
        data = request_data(); data["priorities"]["water_conservation"] = 1
        result = plan(data, TestProvider())
        self.assertTrue(result["candidate_rotations"])
        self.assertEqual(result["ranking"]["status"], "partial_ranking")
        self.assertIn("water_conservation", result["ranking"]["unavailable_priorities"])
        for candidate in result["candidate_rotations"]:
            self.assertIn("rank", candidate)
            for name in ("water_resilience", "salinity_risk", "stage_stress", "soil_health_contribution", "income", "low_input_cost"):
                dimension = candidate["dimension_results"][name]
                self.assertEqual(dimension["status"], "insufficient_data")
                self.assertIsNone(dimension["value"])

    def test_missing_ph_is_unknown_and_confidence_limited(self):
        data = request_data(); data["soil"] = {}
        result = plan(data, TestProvider())
        for c in result["candidate_rotations"]:
            self.assertIsNone(c["dimension_results"]["soil_suitability"]["value"])
            self.assertEqual(c["evidence_confidence"]["label"], "limited")

    def test_nasa_location_and_temperature_change_interpretation_and_ranking(self):
        class LocationProvider(TestProvider):
            def profile(self, latitude, longitude, start, end):
                self.temperature = 8 if latitude > 25 else 22
                return super().profile(latitude, longitude, start, end)
        data = request_data(); provider = LocationProvider()
        warm = plan(data, provider)
        data["location"]["latitude"] = 25.6
        cold = plan(data, provider)
        warm_values = {r["crop_id"]: r["climate_suitability"]["value"] for r in warm["crop_comparisons"]}
        cold_values = {r["crop_id"]: r["climate_suitability"]["value"] for r in cold["crop_comparisons"]}
        self.assertNotEqual(warm_values, cold_values)
        self.assertEqual(warm_values["maize"], "good_fit")
        self.assertEqual(cold_values["maize"], "potential_concern")
        self.assertEqual(cold_values["sunflower"], "acceptable")
        for candidate in cold["candidate_rotations"]:
            sources = candidate["dimension_results"]["climate_suitability"]["components"]
            for component in sources:
                source = component["environment_source"]
                self.assertEqual(source["parameter"], "T2M")
                self.assertEqual(source["unit"], "degC")
                self.assertIn("period", source)
                self.assertIn("crop_requirement_used", component)

    def test_confidence_rules_are_deterministic_without_optional_requirements(self):
        self.assertEqual(confidence(["verified"] * 5), "high")
        self.assertEqual(confidence(["verified", "provisional"]), "moderate")
        for state in ("unresolved", "missing"):
            self.assertEqual(confidence(["verified", state]), "limited")
        self.assertEqual(confidence(["verified"], context_incomplete=True), "limited")

    def test_calendar_month_nasa_changes_can_reorder_actual_rotation_options(self):
        class SeasonalProvider(TestProvider):
            def profile(self, latitude, longitude, start, end):
                profile = super().profile(latitude, longitude, start, end)
                points = []
                for offset in range(366):
                    day = date(2024, 1, 1) + timedelta(days=offset)
                    value = 34 if latitude > 25 and day.month in (4, 5) else 22
                    points.append({"date": day.isoformat(), "value": value})
                profile["series"]["T2M"]["daily"] = points
                profile["coverage"]["T2M"] = {"complete": True, "valid_days": 366, "expected_days": 366}
                return profile
        data = request_data(); data["priorities"] = {"climate_suitability": 1}
        warm = plan(data, SeasonalProvider())
        data["location"]["latitude"] = 25.6
        hot = plan(data, SeasonalProvider())
        ranks_before = {c["id"]: c["rank"] for c in warm["candidate_rotations"]}
        ranks_after = {c["id"]: c["rank"] for c in hot["candidate_rotations"]}
        self.assertNotEqual(ranks_before, ranks_after)
        self.assertLess(ranks_after["rotation-sunflower-aman_rice-sunflower"], ranks_after["rotation-maize-aman_rice-maize"])
        self.assertTrue(all(c["evidence_confidence"]["label"] == "moderate" for c in hot["candidate_rotations"]))

    def test_farmer_priority_and_soil_can_change_real_options(self):
        data = request_data(); data["soil"]["ph"] = 5.5
        data["priorities"] = {"soil_suitability": 1}
        result = plan(data, TestProvider())
        by_id = {c["id"]: c for c in result["candidate_rotations"]}
        self.assertLess(by_id["rotation-maize-aman_rice-maize"]["rank"], by_id["rotation-sunflower-aman_rice-sunflower"]["rank"])
        data["priorities"] = {"preferred_crops": 1, "soil_suitability": .5}
        result = plan(data, TestProvider())
        self.assertEqual(result["candidate_rotations"][0]["id"], "rotation-sunflower-aman_rice-sunflower")

    def test_no_fixture_dataset_or_dates_can_enter_prototype(self):
        with self.assertRaises(DatasetSafetyError):
            load_dataset("prototype_recommendation", path=ROOT / "tests/fixtures/development_knowledge.json")
        result = plan(request_data(), TestProvider())
        text = json.dumps(result)
        self.assertNotIn("DEVELOPMENT_FIXTURE", text)
        self.assertNotIn("synthetic agronomy", text)
        for c in result["candidate_rotations"]:
            for a in c["activities"]:
                self.assertTrue(a["calendar_id"].startswith("VCAL"))
                self.assertTrue(a["calendar_evidence"]["source"]["source_url"].startswith("https://"))

    def test_api_defaults_to_real_prototype_and_requires_declared_scope(self):
        data = request_data(); del data["mode"]
        with patch("next_season.api.views.PowerProvider", return_value=TestProvider()):
            result = Client().post("/api/rotation-plan", data=json.dumps(data), content_type="application/json")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["mode"], "prototype_recommendation")
        self.assertTrue(result.json()["candidate_rotations"])
        del data["location"]["country_code"]
        result = Client().post("/api/rotation-plan", data=json.dumps(data), content_type="application/json")
        self.assertEqual(result.status_code, 400)

    def test_prototype_projection_rejects_stale_source_fingerprints(self):
        with patch("next_season.knowledge.prototype.fingerprint", return_value="changed"):
            with self.assertRaises(DatasetSafetyError):
                load_dataset("prototype_recommendation")
