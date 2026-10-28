"""Offline tests. Synthetic agronomy is isolated in tests/fixtures/."""
import copy
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock,patch

os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django
django.setup()
from django.test import Client,override_settings
from next_season.knowledge.identity import ROOT,resolve,MappingError
from next_season.knowledge.schema import normalize_value
from next_season.knowledge.normalize import build,digest
from next_season.knowledge.repository import load_dataset,DatasetSafetyError,usable
from next_season.environment.power import normalize,query_for,PowerProvider,PowerError,PARAMETERS
from next_season.engine.generation import generate
from next_season.engine.service import plan

TEST_TMP=ROOT/".runtime/test-tmp"
TEST_TMP.mkdir(parents=True,exist_ok=True)
tempfile.tempdir=str(TEST_TMP)


def input_data():
    return {"mode":"development_fixture","location":{"latitude":25.7439,"longitude":89.2752},"historical_period":{"start":"2024-01-01","end":"2024-01-03"},"soil":{"ph":6.1},"crop_history":["aman_rice"],"constraints":{},"horizon":3,"preferred_crop_ids":["sunflower"],"priorities":{"preferred_crops":1,"climate_suitability":0.5}}


def raw_response(temperature=22):
    return {"header":{"fill_value":-999,"title":"Synthetic offline unit-test response"},"geometry":{"coordinates":[89.2752,25.7439,0]},"parameters":{p:{"units":"mm/day" if p=="PRECTOTCORR" else "C"} for p in PARAMETERS},"properties":{"parameter":{p:{d:(2 if p=="PRECTOTCORR" else temperature) for d in ("20240101","20240102","20240103")} for p in PARAMETERS}}}


class TestProvider:
    def __init__(self,temperature=22):self.temperature=temperature
    def profile(self,latitude,longitude,start,end):
        return normalize(raw_response(self.temperature),query_for(latitude,longitude,start,end),retrieved_at="2026-10-28T00:00:00+00:00",cache_status="synthetic_test_only")


class KnowledgeTests(unittest.TestCase):
    def test_namespaces_do_not_join_by_number(self):
        self.assertEqual(resolve("C01","1_crops_master.csv")["canonical_id"],"aman_rice")
        self.assertEqual(resolve("1","5_crop_soil_requirements.csv")["canonical_id"],"mung_bean")
        self.assertEqual(resolve("rice_brri_dhan51","8_crop_rotation_rules.csv")["variety_id"],"brri_dhan51")

    def test_invalid_mapping_rejected(self):
        for raw,namespace in (("C99","1_crops_master.csv"),("1","1_crops_master.csv"),("Oryza sativa L.","1_crops_master.csv")):
            with self.assertRaises(MappingError):resolve(raw,namespace)

    def test_missing_never_zero(self):
        for value in ("N/A","UNKNOWN","", " null "):
            self.assertIsNone(normalize_value(value,"number"))
        self.assertEqual(normalize_value("0","number"),0)
        self.assertIs(normalize_value("FALSE","boolean"),False)
        with self.assertRaises(ValueError):normalize_value("estimated","number")

    def test_raw_integrity_and_all_cells_preserved(self):
        manifest=json.loads((ROOT/"data/normalized/manifest.json").read_text())
        staging=json.loads((ROOT/"data/normalized/staging.json").read_text(encoding="utf-8"))
        self.assertEqual(len(staging["records"]),374)
        for item in manifest["assets"]:self.assertEqual(digest(ROOT/"research/csv"/item["file"]),item["sha256"])
        for row in staging["records"]:
            for key,value in row["raw"].items():
                field=row["fields"][key]
                self.assertEqual(field["raw_value"],value)
                self.assertEqual(field["provenance"]["column"],key)
                if value.strip().lower() in ("n/a",""):self.assertIsNone(field["normalized_value"])

    def test_normalized_crop_fields_keep_variety_separate(self):
        staging=json.loads((ROOT/"data/normalized/staging.json").read_text(encoding="utf-8"))
        record=next(r for r in staging["records"] if r["id"]=="5_crop_soil_requirements.csv:2")
        self.assertEqual(record["fields"]["crop_id"]["raw_value"],"1")
        self.assertEqual(record["fields"]["crop_id"]["normalized_value"],"mung_bean")
        self.assertEqual(record["fields"]["crop_id"]["identity_mapping"]["variety_id"],"bari_mung_6")

    def test_conflicts_not_resolved(self):
        conflicts=json.loads((ROOT/"data/normalized/conflicts.json").read_text())
        self.assertEqual(len(conflicts["conflicts"]),3)
        for conflict in conflicts["conflicts"]:
            self.assertEqual(conflict["claim"]["verification"],"conflicting")
            self.assertFalse(usable(conflict["claim"],"rotation_feasibility"))
            self.assertIsNone(conflict["resolution"])

    def test_production_has_no_usable_calendars(self):
        data=load_dataset()
        self.assertEqual(set(c["id"] for c in data["crops"]),{"aman_rice","maize","sunflower","mung_bean"})
        self.assertTrue(all(cal["verification"]=="provisional" for c in data["crops"] for cal in c["calendars"]))
        self.assertEqual(data["rotation_rules"],[])

    def test_fixture_disabled_by_default_and_rejected_in_production(self):
        path=ROOT/"tests/fixtures/development_knowledge.json"
        with self.assertRaises(DatasetSafetyError):load_dataset("development_fixture")
        with self.assertRaises(DatasetSafetyError):load_dataset("production",path=path)

    def test_fixture_marker_cannot_hide_under_production_origin(self):
        data=load_dataset("development_fixture",allow_fixtures=True)
        data["origin"]="RESEARCH_EVIDENCE"
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"bad.json";path.write_text(json.dumps(data))
            with self.assertRaises(DatasetSafetyError):load_dataset(path=path)


class PowerTests(unittest.TestCase):
    def test_missing_and_units(self):
        raw=raw_response();raw["properties"]["parameter"]["T2M"]["20240101"]=-999
        result=normalize(raw,query_for(25,89,"2024-01-01","2024-01-03"),retrieved_at="test",cache_status="test")
        self.assertIsNone(result["series"]["T2M"]["daily"][0]["value"])
        self.assertFalse(result["coverage"]["T2M"]["complete"])
        raw["parameters"]["T2M"]["units"]="Fahrenheit"
        with self.assertRaises(PowerError):normalize(raw,result["query"],retrieved_at="test",cache_status="test")

    def test_cache_exact_query_and_checksum(self):
        with tempfile.TemporaryDirectory() as tmp:
            session=Mock();session.get.return_value.json.return_value=raw_response()
            provider=PowerProvider(tmp,session)
            first=provider.profile(25,89,"2024-01-01","2024-01-03")
            cached=provider.profile(25,89,"2024-01-01","2024-01-03")
            self.assertEqual(cached["cache_status"],"cached");self.assertEqual(session.get.call_count,1)
            provider.profile(26,89,"2024-01-01","2024-01-03")
            self.assertEqual(session.get.call_count,2)
            self.assertEqual(first["response_sha256"],cached["response_sha256"])

    def test_future_period_and_nonfinite_location_rejected(self):
        with self.assertRaises(ValueError):query_for(float("nan"),89,"2024-01-01","2024-01-03")
        with self.assertRaises(ValueError):query_for(25,89,"2099-01-01","2099-01-03")

    def test_incomplete_series_cannot_gain_climate_category(self):
        raw=raw_response();raw["properties"]["parameter"]["T2M"]["20240101"]=-999
        provider=TestProvider()
        provider.profile=lambda *args:normalize(raw,query_for(25,89,"2024-01-01","2024-01-03"),retrieved_at="test",cache_status="test")
        request=input_data();request["mode"]="production"
        response=plan(request,provider)
        self.assertTrue(all(c["climate_suitability"]["status"]=="insufficient_data" for c in response["crop_comparisons"]))


class EngineTests(unittest.TestCase):
    def run_plan(self,request=None,temperature=22):return plan(request or input_data(),TestProvider(temperature),allow_fixtures=True)

    def test_production_blocks_provisional_calendar_but_returns_real_contract(self):
        request=input_data();request["mode"]="production"
        result=self.run_plan(request)
        self.assertEqual(result["status"],"blocked_scientific_data")
        self.assertEqual(result["candidate_rotations"],[])
        self.assertFalse(result["is_recommendation"])
        self.assertEqual(len(result["crop_comparisons"]),4)

    def test_fixture_end_to_end_and_no_opaque_score(self):
        result=self.run_plan()
        self.assertGreaterEqual(len(result["candidate_rotations"]),2)
        self.assertFalse(result["is_recommendation"])
        self.assertIn("DEVELOPMENT_FIXTURE",result["notice"])
        self.assertNotIn('"overall_score"',json.dumps(result))
        for c in result["candidate_rotations"]:
            self.assertEqual(c["dimension_results"]["water_resilience"]["status"],"insufficient_data")

    def test_hard_exclusion_and_required_crop(self):
        request=input_data();request["constraints"]={"excluded_crop_ids":["maize"],"required_crop_ids":["sunflower"]}
        result=self.run_plan(request)
        self.assertTrue(result["candidate_rotations"])
        for c in result["candidate_rotations"]:
            ids=[a["crop_id"] for a in c["activities"]]
            self.assertNotIn("maize",ids);self.assertIn("sunflower",ids)
            self.assertTrue(all(c["status"]=="satisfied" for c in c["hard_constraints"]))

    def test_locked_slots_and_zero_change_limit(self):
        request=input_data();request["constraints"]={"locked_slots":{"0":"sunflower"},"baseline":["sunflower","maize","aman_rice"],"max_changes":0}
        result=self.run_plan(request)
        self.assertEqual(len(result["candidate_rotations"]),1)
        self.assertEqual([a["crop_id"] for a in result["candidate_rotations"][0]["activities"]],request["constraints"]["baseline"])

    def test_deadline_and_current_crop_occupancy(self):
        request=input_data();request["current_crop"]={"crop_id":"aman_rice","harvest_date":"2027-02-01"}
        self.assertEqual(self.run_plan(request)["candidate_rotations"],[])
        request=input_data();request["constraints"]={"latest_harvest":"2027-07-01"}
        self.assertEqual(self.run_plan(request)["candidate_rotations"],[])

    def test_history_changes_possible_sequences(self):
        request=input_data();request["crop_history"]=["sunflower"]
        self.assertTrue(all(c["activities"][0]["crop_id"]!="sunflower" for c in self.run_plan(request)["candidate_rotations"]))

    def test_priorities_change_ranking(self):
        request=input_data();request["preferred_crop_ids"]=["maize"]
        request["priorities"]={"preferred_crops":1,"rotation_quality":0.5}
        first=self.run_plan(request)["candidate_rotations"][0]
        request["priorities"]={"preferred_crops":0.5,"rotation_quality":1}
        other=self.run_plan(request)["candidate_rotations"][0]
        self.assertNotEqual(first["id"],other["id"])

    def test_power_change_changes_supported_comparison(self):
        request=input_data();request["mode"]="production"
        cold=self.run_plan(request,6);warm=self.run_plan(request,24)
        c={c["crop_id"]:c["climate_suitability"]["value"] for c in cold["crop_comparisons"]}
        w={c["crop_id"]:c["climate_suitability"]["value"] for c in warm["crop_comparisons"]}
        self.assertNotEqual(c,w)
        self.assertEqual(c["aman_rice"],"outside_reference")
        self.assertEqual(w["aman_rice"],"within_optimal_reference")

    def test_soil_change_and_unknown(self):
        request=input_data();request["mode"]="production"
        initial=self.run_plan(request)
        request["soil"]={"ph":8}
        changed=self.run_plan(request)
        self.assertNotEqual(initial["crop_comparisons"][0]["soil_suitability"]["value"],changed["crop_comparisons"][0]["soil_suitability"]["value"])
        request["soil"]={}
        self.assertTrue(all(c["soil_suitability"]["status"]=="insufficient_data" for c in self.run_plan(request)["crop_comparisons"]))

    def test_unavailable_priority_never_silently_reweighted(self):
        request=input_data();request["priorities"]["water_conservation"]=1
        result=self.run_plan(request)
        self.assertEqual(result["ranking"]["status"],"insufficient_data")
        self.assertTrue(all("rank" not in c for c in result["candidate_rotations"]))

    def test_provenance_reaches_explanations(self):
        result=self.run_plan()
        climate=next(e for e in result["candidate_rotations"][0]["explanations"] if e["dimension"]=="climate_suitability")
        evidence=climate["agronomic_evidence"][0]
        self.assertIn("raw_value",evidence);self.assertIn("normalized_value",evidence)
        self.assertIn("provenance",evidence);self.assertIn("source",evidence)
        self.assertIn("response_sha256",result["candidate_rotations"][0]["dimension_results"]["climate_suitability"]["components"][0]["environment_source"])


class ApiTests(unittest.TestCase):
    def setUp(self):self.client=Client()
    def post(self,data):return self.client.post("/api/rotation-plan",data=json.dumps(data),content_type="application/json")

    @patch("next_season.api.views.PowerProvider",return_value=TestProvider())
    def test_production_endpoint(self,_):
        request=input_data();request["mode"]="production"
        response=self.post(request)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()["status"],"blocked_scientific_data")

    @override_settings(DEBUG=False,ALLOW_DEVELOPMENT_FIXTURES=True)
    def test_fixture_cannot_enter_production_server(self):
        self.assertEqual(self.post(input_data()).status_code,403)

    @override_settings(DEBUG=True,ALLOW_DEVELOPMENT_FIXTURES=True)
    @patch("next_season.api.views.PowerProvider",return_value=TestProvider())
    def test_explicit_local_fixture_endpoint(self,_):
        result=self.post(input_data())
        self.assertEqual(result.status_code,200)
        self.assertEqual(result.json()["status"],"development_fixture_results")

    def test_unknown_values_and_all_zero_priorities(self):
        bad=input_data();bad["unknown_field"]={}
        self.assertEqual(self.post(bad).status_code,400)
        bad=input_data();bad["priorities"]={"preferred_crops":0}
        self.assertEqual(self.post(bad).status_code,400)
        bad=input_data();bad["crop_history"]=["C01"]
        self.assertEqual(self.post(bad).status_code,400)

    def test_client_cannot_inject_calendars_or_conflicting_limits(self):
        bad=input_data();bad["calendars"]=[]
        self.assertEqual(self.post(bad).status_code,400)
        bad=input_data();bad["constraints"]={"required_crop_ids":["maize"],"excluded_crop_ids":["maize"]}
        self.assertEqual(self.post(bad).status_code,400)


if __name__=="__main__":unittest.main()
