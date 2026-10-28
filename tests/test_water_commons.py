"""Water Commons uses only explicitly supplied irrigation plans; test values are synthetic user inputs."""
import copy
from datetime import date
import json
import os
import unittest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.test import Client
from next_season.engine.water_commons import CommonsError, analyze_community, options_for, weeks_between


PLAN = {"country_code": "BD", "crop_history": [], "constraints": {}, "horizon": 3}


def farm(identifier, numeric=True, locked=False):
    option = options_for(PLAN)[0]
    activities = []
    for index, activity in enumerate(option["activities"]):
        planting = date.fromisoformat(activity["planting_window"]["start"] + "-15")
        harvest = date.fromisoformat(activity["harvest_window"]["start"] + "-15")
        values = [0.0] * len(list(weeks_between(planting, harvest)))
        if index == 0:
            values[0] = 8.0
        activities.append({"crop_id": activity["crop_id"], "planting_date": planting,
            "harvest_date": harvest, "weekly_irrigation_m3": values if numeric else None,
            "timing_locked": locked, "water_plan_source": "Test farmer's planned delivery schedule"})
    return {"farm_id": identifier, "farm_name": "Farm " + identifier, "area_ha": 1.0,
        "plan": copy.deepcopy(PLAN), "selected_rotation_id": option["id"],
        "activities": activities, "flexibility_weeks": 1}


def group(numeric=True, locked=False):
    return {"group_name": "Test irrigation group", "capacity_m3_per_week": 10.0,
        "capacity_unit": "m3/week", "time_resolution": "week", "capacity_source": "Test group declaration",
        "farms": [farm("a", numeric=numeric, locked=locked), farm("b", locked=locked)]}


class WaterCommonsTests(unittest.TestCase):
    def test_multiple_farms_sum_and_detect_exact_conflict(self):
        result = analyze_community(group())
        self.assertEqual(result["original_profile"]["status"], "quantitative_plan_comparison")
        self.assertEqual(result["original_profile"]["peak_m3"], 16.0)
        self.assertEqual(result["conflict_windows"][0]["excess_m3"], 6.0)
        self.assertEqual(result["conflict_windows"][0]["contributing_farms"], ["a", "b"])
        self.assertEqual(result["capacity"]["unit"], "m3/week")

    def test_feasible_week_shift_reduces_peak_without_changing_total(self):
        result = analyze_community(group())
        self.assertTrue(result["suggested_adjustments"])
        suggestion = result["suggested_adjustments"][0]
        self.assertEqual(suggestion["type"], "planting_window_shift")
        self.assertEqual(suggestion["before_peak_m3"], 16.0)
        self.assertEqual(suggestion["after_peak_m3"], 8.0)
        self.assertEqual(suggestion["total_water_change_m3"], 0.0)
        self.assertEqual(suggestion["adjusted_profile"]["total_planned_m3"], result["original_profile"]["total_planned_m3"])
        self.assertEqual(suggestion["adjusted_profile"]["conflicts"], [])

    def test_locked_timing_prevents_all_shift_suggestions(self):
        result = analyze_community(group(locked=True))
        self.assertTrue(result["conflict_windows"])
        self.assertEqual(result["suggested_adjustments"], [])

    def test_missing_volume_never_becomes_zero_or_capacity_conflict(self):
        result = analyze_community(group(numeric=False))
        self.assertEqual(result["original_profile"]["status"], "qualitative_overlap_only")
        self.assertIsNone(result["original_profile"]["peak_m3"])
        self.assertTrue(result["qualitative_overlap_windows"])
        self.assertEqual(result["conflict_windows"], [])
        self.assertEqual(result["suggested_adjustments"], [])
        self.assertTrue(all(row["community_m3"] is None for row in result["original_profile"]["rows"]))

    def test_unapproved_rotation_and_constraint_are_rejected(self):
        data=group()
        data["farms"][0]["selected_rotation_id"]="made-up-rotation"
        with self.assertRaises(CommonsError):analyze_community(data)
        data=group()
        data["farms"][0]["plan"]["constraints"]={"excluded_crop_ids":["aman_rice"]}
        with self.assertRaises(CommonsError):analyze_community(data)

    def test_provenance_and_api_response(self):
        payload=group()
        result=analyze_community(payload)
        source=result["farms"][0]["activity_provenance"][0]["water_evidence"]
        self.assertEqual(source["basis"], "farmer_entered_delivered_irrigation_plan")
        self.assertEqual(source["crop_water_requirement"], "insufficient_data")
        self.assertEqual(source["rainfall_contribution"], "not_subtracted")
        client=Client()
        response=client.post("/api/water-commons/options",data=json.dumps({"plan":PLAN}),content_type="application/json")
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()["options"][0]["id"],payload["farms"][0]["selected_rotation_id"])
        response=client.post("/api/water-commons/analyze",data=json.dumps(payload,default=lambda value:value.isoformat()),content_type="application/json")
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()["farms"][0]["activity_provenance"][0]["water_evidence"]["basis"],"farmer_entered_delivered_irrigation_plan")

    def test_frontend_dated_event_shape_aggregates_only_declared_complete_plans(self):
        payload = group(numeric=False)
        for item in payload["farms"]:
            for index, activity in enumerate(item["activities"]):
                activity.pop("weekly_irrigation_m3")
                activity["schedule_complete"] = True
                activity["weekly_irrigation_events"] = []
                if index == 0:
                    monday = next(weeks_between(activity["planting_date"], activity["harvest_date"]))
                    activity["weekly_irrigation_events"] = [{"week_start": monday, "volume_m3": 8.0}]
        response = Client().post("/api/water-commons/analyze", data=json.dumps(payload, default=lambda value: value.isoformat()), content_type="application/json")
        self.assertEqual(response.status_code, 200, response.content)
        result = response.json()
        self.assertEqual(result["original_profile"]["status"], "quantitative_plan_comparison")
        self.assertEqual(result["original_profile"]["peak_m3"], 16.0)
        self.assertEqual(result["original_profile"]["total_planned_m3"], 16.0)
        self.assertEqual(result["conflict_windows"][0]["excess_m3"], 6.0)

    def test_incomplete_dated_events_cannot_be_treated_as_zero(self):
        payload = group(numeric=False)
        activity = payload["farms"][0]["activities"][0]
        activity.pop("weekly_irrigation_m3")
        activity["schedule_complete"] = False
        activity["weekly_irrigation_events"] = [{"week_start": next(weeks_between(activity["planting_date"], activity["harvest_date"])), "volume_m3": 8.0}]
        response = Client().post("/api/water-commons/analyze", data=json.dumps(payload, default=lambda value: value.isoformat()), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_three_and_five_farm_groups_use_same_aggregation_contract(self):
        for count in (3, 5):
            payload = group()
            payload["farms"] = [farm(str(index)) for index in range(count)]
            result = analyze_community(payload)
            self.assertEqual(len(result["farms"]), count)
            self.assertEqual(result["original_profile"]["peak_m3"], 8.0 * count)
            self.assertEqual(result["conflict_windows"][0]["excess_m3"], 8.0 * count - 10.0)

    def test_no_conflict_when_entered_capacity_covers_peak(self):
        payload = group()
        payload["capacity_m3_per_week"] = 16.0
        result = analyze_community(payload)
        self.assertEqual(result["conflict_windows"], [])
        self.assertEqual(result["suggested_adjustments"], [])
