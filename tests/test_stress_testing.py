"""Historical stress tests against recorded, checksummed public NASA POWER responses."""

import json
from pathlib import Path
import unittest
from unittest.mock import patch

from django.test import Client

from test_prototype import request_data
from next_season.engine.service import plan
from next_season.engine.stress_testing import SCENARIOS, YEARS, build_stress_tests, robustness
from next_season.environment.power import checksum, normalize
from next_season.environment.profile import EnvironmentalProfile
from next_season.knowledge.repository import load_dataset

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class RecordedPower:
    def __init__(self, name="khulna", missing_year=None):
        path = FIXTURES / f"nasa_power_{name}_2015_2024.json"
        self.recording = json.loads(path.read_text(encoding="utf-8"))
        self.missing_year = missing_year
        self.records = {item["year"]: item for item in self.recording["records"]}

    def profile(self, latitude, longitude, start, end):
        year = int(start[:4])
        record = self.records[year]
        if (latitude, longitude) != (self.recording["location"]["latitude"], self.recording["location"]["longitude"]):
            raise ValueError("Recorded NASA response belongs to a different point")
        if (start, end) != (f"{year}-01-01", f"{year}-12-31"):
            raise ValueError("Recorded NASA response belongs to a different period")
        if checksum(record["raw_response"]) != record["response_sha256"]:
            raise ValueError("Recorded NASA source checksum mismatch")
        result = normalize(record["raw_response"], record["query"], retrieved_at="2026-10-28T00:00:00+00:00", cache_status="recorded_public_nasa_fixture")
        if year == self.missing_year:
            result["series"]["PRECTOTCORR"]["daily"][0]["value"] = None
            result["coverage"]["PRECTOTCORR"]["complete"] = False
            result["coverage"]["PRECTOTCORR"]["valid_days"] -= 1
        return result


class Unavailable:
    def profile(self, *args):
        raise RuntimeError("Test-only provider unavailability")


class StressTestingTests(unittest.TestCase):
    def test_real_power_fixture_integrity_and_complete_baseline(self):
        provider = RecordedPower()
        self.assertEqual(set(provider.records), set(YEARS))
        for year in YEARS:
            record = provider.records[year]
            self.assertEqual(checksum(record["raw_response"]), record["response_sha256"])
            profile = provider.profile(22.8, 89.55, f"{year}-01-01", f"{year}-12-31")
            self.assertTrue(all(value["complete"] for value in profile["coverage"].values()))
            self.assertEqual(profile["response_sha256"], record["response_sha256"])

    def test_scenarios_use_observed_years_and_distinct_dry_wet_hot_evidence(self):
        request = request_data(); request["historical_period"] = {"start":"2024-01-01","end":"2024-12-31"}
        result = plan(request, RecordedPower())
        scenarios = result["stress_tests"]
        self.assertEqual({name:scenarios[name]["selected_year"] for name in SCENARIOS},
                         {"historical_normal":2024,"historical_dry":2022,"historical_hot":2016,"historical_wet":2017})
        self.assertLess(scenarios["historical_dry"]["environmental_conditions"]["annual_precipitation_mm"],
                        scenarios["historical_wet"]["environmental_conditions"]["annual_precipitation_mm"])
        self.assertGreater(scenarios["historical_hot"]["environmental_conditions"]["annual_mean_t2m_c"],
                           scenarios["historical_normal"]["environmental_conditions"]["annual_mean_t2m_c"])
        for name in SCENARIOS:
            item = scenarios[name]
            year = item["selected_year"]
            self.assertEqual(item["provenance"]["response_sha256"], RecordedPower().records[year]["response_sha256"])
            self.assertEqual(item["provenance"]["period"], {"start":f"{year}-01-01","end":f"{year}-12-31"})
            self.assertEqual(item["provenance"]["variables"], ["T2M","T2M_MIN","T2M_MAX","PRECTOTCORR"])
            for interpretation in item["rotation_interpretation"].values():
                self.assertTrue(all(v["status"] == "insufficient_data" for v in interpretation["unsupported_dimensions"].values()))
        self.assertIn("not a forecast", scenarios["notice"])

    def test_second_real_location_changes_scenario_years(self):
        crops = {crop["id"]:crop for crop in load_dataset("prototype_recommendation")["crops"]}
        khulna = build_stress_tests(22.8, 89.55, RecordedPower(), [], crops)
        dinajpur = build_stress_tests(25.63, 88.65, RecordedPower("dinajpur"), [], crops)
        self.assertNotEqual(khulna["historical_dry"]["selected_year"], dinajpur["historical_dry"]["selected_year"])
        self.assertNotEqual(khulna["historical_wet"]["selected_year"], dinajpur["historical_wet"]["selected_year"])
        self.assertEqual(dinajpur["historical_dry"]["selected_year"], 2015)
        self.assertEqual(dinajpur["historical_wet"]["selected_year"], 2020)

    def test_missing_observation_is_not_zero_or_a_scenario(self):
        crops = {crop["id"]:crop for crop in load_dataset("prototype_recommendation")["crops"]}
        result = build_stress_tests(22.8,89.55,RecordedPower(missing_year=2022),[],crops)
        self.assertEqual(result["baseline"]["status"], "insufficient_data")
        self.assertEqual(result["baseline"]["missing_years"], [2022])
        for name in SCENARIOS:
            self.assertEqual(result[name]["evidence_status"], "insufficient_data")
            self.assertIsNone(result[name]["environmental_conditions"])

    def test_robustness_labels_count_distinct_observed_years(self):
        candidates = [{"id":"one"},{"id":"two"},{"id":"three"}]
        years = {"historical_normal":2024,"historical_dry":2022,"historical_hot":2022,"historical_wet":2017}
        values = {"one":["good_fit","acceptable","acceptable","good_fit"],
                  "two":["good_fit","potential_concern","potential_concern","acceptable"],
                  "three":["potential_concern","potential_concern","potential_concern","acceptable"]}
        scenarios = {name:{"evidence_status":"supported","selected_year":years[name],
                           "rotation_interpretation":{key:{"status":"qualitative_screening","value":items[i]}
                                                      for key,items in values.items()}} for i,name in enumerate(SCENARIOS)}
        result = robustness(scenarios,candidates)
        self.assertEqual([result["by_candidate"][key]["label"] for key in ("one","two","three")],
                         ["robust","moderately_robust","sensitive"])
        self.assertEqual(result["most_robust_candidate_ids"],["one"])

    def test_api_preserves_scenario_source_provenance(self):
        provider = RecordedPower()
        request = request_data(); request["historical_period"] = {"start":"2024-01-01","end":"2024-12-31"}
        environment = EnvironmentalProfile(FIXTURES, power=provider, smap=Unavailable(), gpm=Unavailable())
        with patch("next_season.api.views.PowerProvider", return_value=provider), patch("next_season.api.views.environmental_provider", return_value=environment):
            response = Client().post("/api/rotation-plan", data=json.dumps(request), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        stress = payload["stress_tests"]
        self.assertEqual(stress["historical_dry"]["provenance"]["response_sha256"], provider.records[2022]["response_sha256"])
        self.assertEqual(stress["historical_dry"]["provenance"]["provider"], "NASA POWER")
        self.assertEqual(stress["robustness"]["by_candidate"].keys(),
                         {item["id"] for item in payload["candidate_rotations"]})
