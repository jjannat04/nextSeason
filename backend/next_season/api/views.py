from datetime import date
import json
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import PlanInput,EnvironmentInput,CommonsOptionsInput,WaterCommonsInput
from ..engine.service import plan
from ..environment.power import PowerProvider,PowerError
from ..knowledge.repository import DatasetSafetyError


def environmental_provider(power=None):
    from ..environment.profile import EnvironmentalProfile
    return EnvironmentalProfile(settings.ROOT/".runtime",power=power or PowerProvider(settings.POWER_CACHE_DIR),satellite_cache_dir=settings.ENVIRONMENT_CACHE_DIR)


@api_view(["POST"])
def environment_profile(request):
    serializer=EnvironmentInput(data=request.data)
    serializer.is_valid(raise_exception=True)
    inputs=json.loads(json.dumps(serializer.validated_data,default=lambda obj:obj.isoformat()))
    location=inputs["location"];period=inputs["historical_period"]
    return Response(environmental_provider().profile(location["latitude"],location["longitude"],period["start"],period["end"],inputs.get("rainfall_comparison_period")))


@api_view(["GET"])
def health(request):
    from ..knowledge.repository import load_dataset
    from ..engine.month_generation import eligible_crop
    try:
        data=load_dataset("prototype_recommendation")
        eligible=[c["id"] for c in data["crops"] if eligible_crop(c)]
    except (DatasetSafetyError,OSError,ValueError):
        eligible=[]
    return Response({"status":"ok","milestone":"prototype.1","fixtures_enabled":bool(settings.DEBUG and settings.ALLOW_DEVELOPMENT_FIXTURES),"recommendation_mode":"prototype_recommendation","eligible_crop_ids":eligible,"prototype_status":"enabled" if len(eligible)>=3 else "blocked_scientific_data"})


@api_view(["POST"])
def rotation_plan(request):
    serializer=PlanInput(data=request.data)
    serializer.is_valid(raise_exception=True)
    # Date fields cross the domain boundary in explicit ISO form.
    inputs=json.loads(json.dumps(serializer.validated_data,default=lambda obj:obj.isoformat() if isinstance(obj,date) else str(obj)))
    try:
        power=PowerProvider(settings.POWER_CACHE_DIR)
        result=plan(inputs,power,allow_fixtures=settings.DEBUG and settings.ALLOW_DEVELOPMENT_FIXTURES,environmental_provider=environmental_provider(power) if inputs["mode"]=="prototype_recommendation" else None)
    except DatasetSafetyError as exc:
        return Response({"error":"dataset_safety","detail":str(exc)},status=403)
    except PowerError as exc:
        return Response({"error":"environment_unavailable","detail":str(exc),"environment_profile":{"status":"unavailable"},"candidate_rotations":[],"data_gaps":[{"dimension":"environment","status":"insufficient_data"}]},status=503)
    return Response(result)


@api_view(["POST"])
def water_commons_options(request):
    from ..engine.water_commons import options_for
    serializer=CommonsOptionsInput(data=request.data)
    serializer.is_valid(raise_exception=True)
    options=options_for(serializer.validated_data["plan"])
    return Response({"status":"available" if options else "no_eligible_rotation", "options":options,
        "limitations":["Bangladesh prototype month-level calendars and conditional systems; exact dates and irrigation volumes are not generated here."]})


@api_view(["POST"])
def water_commons_analyze(request):
    from ..engine.water_commons import analyze_community,CommonsError
    serializer=WaterCommonsInput(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        result=analyze_community(serializer.validated_data)
    except CommonsError as error:
        return Response({"error":"invalid_water_commons_plan","detail":str(error)},status=400)
    return Response(result)
