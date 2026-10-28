from datetime import date
import math
from rest_framework import serializers
from ..knowledge.identity import SLICE
from ..engine.ranking import PRIORITIES


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self,data):
        if not isinstance(data,dict):raise serializers.ValidationError("Expected an object")
        extra=set(data)-set(self.fields)
        if extra:raise serializers.ValidationError({k:"Unknown field" for k in sorted(extra)})
        return super().to_internal_value(data)


class Location(StrictSerializer):
    latitude=serializers.FloatField(min_value=-90,max_value=90)
    longitude=serializers.FloatField(min_value=-180,max_value=180)
    country_code=serializers.ChoiceField(choices=["BD"],required=False)

    def validate(self,attrs):
        if not all(math.isfinite(attrs[k]) for k in ("latitude","longitude")):raise serializers.ValidationError("Coordinates must be finite")
        return attrs


class Period(StrictSerializer):
    start=serializers.DateField()
    end=serializers.DateField()

    def validate(self,attrs):
        if not 0<=(attrs["end"]-attrs["start"]).days<=365 or attrs["end"]>=date.today():
            raise serializers.ValidationError("Use a past historical interval of at most 366 days")
        return attrs


def validate_comparison(attrs):
    comparison=attrs.get("rainfall_comparison_period")
    if comparison:
        selected=attrs["historical_period"]
        if comparison["end"]>=selected["start"] or any(comparison[k].strftime("%m-%d")!=selected[k].strftime("%m-%d") for k in ("start","end")):
            raise serializers.ValidationError({"rainfall_comparison_period":"Use an earlier historical window with matching start/end calendar month-days; this is a comparison window, not a climate normal."})
    return attrs


class EnvironmentInput(StrictSerializer):
    location=Location()
    historical_period=Period()
    rainfall_comparison_period=Period(required=False,allow_null=True)

    def validate(self,attrs):
        return validate_comparison(attrs)


class Soil(StrictSerializer):
    ph=serializers.FloatField(min_value=0,max_value=14,required=False,allow_null=True)
    ph_method=serializers.ChoiceField(choices=["water","KCl","CaCl2","unspecified"],default="unspecified")
    texture=serializers.ChoiceField(choices=["unknown","loam","silt_loam","clay_loam","sandy_loam","clay"],default="unknown")
    salinity_ece_ds_m=serializers.FloatField(min_value=0,required=False,allow_null=True)

    def validate(self,attrs):
        if any(isinstance(v,float) and not math.isfinite(v) for v in attrs.values()):raise serializers.ValidationError("Soil numbers must be finite")
        return attrs


class CurrentCrop(StrictSerializer):
    crop_id=serializers.ChoiceField(choices=SLICE)
    harvest_date=serializers.DateField()

    def validate_harvest_date(self,value):
        if value<date.today():raise serializers.ValidationError("Use crop_history for already harvested crops")
        return value


class Constraints(StrictSerializer):
    required_crop_ids=serializers.ListField(child=serializers.ChoiceField(choices=SLICE),max_length=4,default=list)
    excluded_crop_ids=serializers.ListField(child=serializers.ChoiceField(choices=SLICE),max_length=4,default=list)
    locked_slots=serializers.DictField(child=serializers.ChoiceField(choices=SLICE),default=dict)
    baseline=serializers.ListField(child=serializers.ChoiceField(choices=SLICE),max_length=3,default=list)
    max_changes=serializers.IntegerField(min_value=0,max_value=3,required=False,allow_null=True)
    earliest_planting=serializers.DateField(required=False)
    latest_harvest=serializers.DateField(required=False)

    def validate(self,attrs):
        if set(attrs["required_crop_ids"])&set(attrs["excluded_crop_ids"]):raise serializers.ValidationError("A crop cannot be required and excluded")
        if set(attrs["locked_slots"].values())&set(attrs["excluded_crop_ids"]):raise serializers.ValidationError("A locked crop cannot be excluded")
        if any(k not in ("0","1","2") for k in attrs["locked_slots"]):raise serializers.ValidationError("Locked slot keys are 0, 1 or 2")
        if attrs.get("earliest_planting") and attrs.get("latest_harvest") and attrs["earliest_planting"]>=attrs["latest_harvest"]:raise serializers.ValidationError("Planting must precede harvest deadline")
        return attrs


class PlanInput(StrictSerializer):
    mode=serializers.ChoiceField(choices=["prototype_recommendation","production","development_fixture"],default="prototype_recommendation")
    location=Location()
    historical_period=Period()
    rainfall_comparison_period=Period(required=False,allow_null=True)
    soil=Soil(default=dict)
    crop_history=serializers.ListField(child=serializers.ChoiceField(choices=SLICE),max_length=6,default=list)
    current_crop=CurrentCrop(required=False,allow_null=True)
    constraints=Constraints(default=dict)
    preferred_crop_ids=serializers.ListField(child=serializers.ChoiceField(choices=SLICE),max_length=4,default=list)
    priorities=serializers.DictField(child=serializers.FloatField(min_value=0,max_value=1))
    horizon=serializers.IntegerField(min_value=2,max_value=3,default=3)

    def validate(self,attrs):
        validate_comparison(attrs)
        if attrs["mode"]=="prototype_recommendation" and attrs["location"].get("country_code")!="BD":
            raise serializers.ValidationError({"location":"Declare country_code BD for a Bangladesh location; these calendars do not cover other countries."})
        weights=attrs["priorities"]
        if set(weights)-set(PRIORITIES):raise serializers.ValidationError({"priorities":"Unknown priority key"})
        if not weights or not all(math.isfinite(v) for v in weights.values()) or not any(v>0 for v in weights.values()):raise serializers.ValidationError({"priorities":"At least one finite nonzero priority is required"})
        limits=attrs.get("constraints",{})
        if limits.get("max_changes") is not None and len(limits.get("baseline",[]))!=attrs["horizon"]:raise serializers.ValidationError("A complete baseline is required to limit changes")
        if any(int(k)>=attrs["horizon"] for k in limits.get("locked_slots",{})):raise serializers.ValidationError("Locked slot outside planning horizon")
        return attrs


class CommonsPlan(StrictSerializer):
    country_code=serializers.ChoiceField(choices=["BD"],default="BD")
    crop_history=serializers.ListField(child=serializers.ChoiceField(choices=SLICE),max_length=6,default=list)
    current_crop=CurrentCrop(required=False,allow_null=True)
    constraints=Constraints(default=dict)
    horizon=serializers.IntegerField(min_value=3,max_value=3,default=3)

    def validate(self,attrs):
        limits=attrs.get("constraints",{})
        if limits.get("max_changes") is not None and len(limits.get("baseline",[]))!=3:
            raise serializers.ValidationError("A complete three-crop baseline is required to limit changes")
        return attrs


class CommonsOptionsInput(StrictSerializer):
    plan=CommonsPlan()


class CommonsIrrigationEvent(StrictSerializer):
    week_start=serializers.DateField()
    volume_m3=serializers.FloatField(min_value=0)


class CommonsActivity(StrictSerializer):
    crop_id=serializers.ChoiceField(choices=SLICE)
    planting_date=serializers.DateField()
    harvest_date=serializers.DateField()
    weekly_irrigation_m3=serializers.ListField(child=serializers.FloatField(min_value=0),allow_null=True,required=False)
    weekly_irrigation_events=serializers.ListField(child=CommonsIrrigationEvent(),required=False)
    schedule_complete=serializers.BooleanField(default=False)
    timing_locked=serializers.BooleanField(default=False)
    water_plan_source=serializers.CharField(max_length=160,allow_blank=True,required=False)

    def validate(self,attrs):
        if attrs["harvest_date"]<=attrs["planting_date"]:
            raise serializers.ValidationError("Harvest must follow planting")
        values=attrs.get("weekly_irrigation_m3")
        if values is not None and any(not math.isfinite(value) for value in values):
            raise serializers.ValidationError("Weekly volumes must be finite")
        if values is not None and attrs.get("weekly_irrigation_events"):
            raise serializers.ValidationError("Use either a complete weekly series or dated events")
        events=attrs.get("weekly_irrigation_events",[])
        if events and not attrs["schedule_complete"]:
            raise serializers.ValidationError("Dated events require an explicit complete-schedule declaration")
        if any(not math.isfinite(event["volume_m3"]) for event in events):
            raise serializers.ValidationError("Event volumes must be finite")
        return attrs


class CommonsFarm(StrictSerializer):
    farm_id=serializers.RegexField(r"^[a-zA-Z0-9_-]{1,32}$")
    farm_name=serializers.CharField(max_length=80)
    area_ha=serializers.FloatField(min_value=0.000001)
    plan=CommonsPlan()
    selected_rotation_id=serializers.CharField(max_length=160)
    activities=serializers.ListField(child=CommonsActivity(),min_length=3,max_length=3)
    flexibility_weeks=serializers.IntegerField(min_value=0,max_value=4,default=0)

    def validate(self,attrs):
        if not math.isfinite(attrs["area_ha"]):
            raise serializers.ValidationError("Area must be finite")
        return attrs


class WaterCommonsInput(StrictSerializer):
    group_name=serializers.CharField(max_length=100)
    capacity_m3_per_week=serializers.FloatField(min_value=0.000001)
    capacity_unit=serializers.ChoiceField(choices=["m3/week"])
    time_resolution=serializers.ChoiceField(choices=["week"])
    capacity_source=serializers.CharField(max_length=160,allow_blank=True,required=False)
    farms=serializers.ListField(child=CommonsFarm(),min_length=2,max_length=5)

    def validate(self,attrs):
        if not math.isfinite(attrs["capacity_m3_per_week"]):
            raise serializers.ValidationError("Capacity must be finite")
        ids=[farm["farm_id"] for farm in attrs["farms"]]
        if len(ids)!=len(set(ids)):
            raise serializers.ValidationError("Farm identifiers must be unique")
        return attrs
