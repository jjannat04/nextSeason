from .generation import generate,calendar_ready
from .evaluation import assess_crop,evaluate,insufficient,UNSUPPORTED
from .ranking import rank
from ..knowledge.repository import load_dataset

DISCLAIMER="Next Season is a decision-support research prototype. Results combine NASA Earth observations with published agricultural references and farmer-provided information. Local cultivar, field measurements, and agronomic guidance may change the result."


def prototype_plan(request,provider,environmental_provider=None):
    from .month_generation import generate_months,eligible_crop
    from .prototype_evaluation import assess,evaluate as evaluate_prototype,GAP_REASONS
    data=load_dataset("prototype_recommendation")
    if request["location"].get("country_code")!="BD":
        from ..knowledge.repository import DatasetSafetyError
        raise DatasetSafetyError("Prototype calendars cover Bangladesh. Declare country_code BD for a Bangladesh location; other countries are outside this release.")
    location=request["location"];period=request["historical_period"]
    space=environmental_provider.profile(location["latitude"],location["longitude"],period["start"],period["end"],request.get("rainfall_comparison_period")) if environmental_provider else None
    environment=space["power"] if space else provider.profile(location["latitude"],location["longitude"],period["start"],period["end"])
    if environment.get("status")!="available":
        from ..environment.power import PowerError
        raise PowerError("POWER temperature observations are unavailable; inspect the unified environmental profile for independent provider statuses.")
    crops={c["id"]:c for c in data["crops"]}
    comparisons=[assess(c,environment,request.get("soil",{})) for c in crops.values()]
    candidates,rejected=generate_months(data,request)
    evaluated=[evaluate_prototype(c,crops,environment,request,space_profile=space) for c in candidates]
    ranked,ranking=rank(evaluated,request["priorities"],allow_partial=True)
    from .stress_testing import build_stress_tests
    stress_tests=build_stress_tests(location["latitude"],location["longitude"],provider,ranked,crops) if ranked else None
    gaps=[{"dimension":key,"status":"insufficient_data","message":reason} for key,reason in GAP_REASONS.items()]
    if space:
        gaps += [{"dimension":"provider_"+name,"status":"unavailable","message":("SMAP soil-moisture" if name=="smap" else "GPM IMERG rainfall")+" observations are unavailable. Their contribution was not scored; exact provider status remains in the NASA profile."} for name,value in space["provider_status"].items() if value["status"]!="available"]
    for crop in crops.values():
        if not eligible_crop(crop):
            gaps.append({"dimension":"calendar_"+crop["id"],"status":"insufficient_data","message":crop.get("prototype_exclusion") or "Required crop evidence unavailable"})
    if request.get("soil",{}).get("ph") is None:
        gaps.append({"dimension":"soil_suitability","status":"insufficient_data","message":"Field pH is unknown; no zero or regional default was substituted."})
    return {"status":"rotation_options" if ranked else "no_feasible_rotation","mode":"prototype_recommendation","dataset_origin":data["origin"],
        "is_recommendation":bool(ranked),"notice":DISCLAIMER,"environment_profile":environment,"space_profile":space,"candidate_rotations":ranked,"stress_tests":stress_tests,
        "crop_comparisons":comparisons,"eligible_crop_ids":[c["id"] for c in crops.values() if eligible_crop(c)],
        "sequence_evidence_coverage":data["sequence_evidence_coverage"],
        "ranking":ranking,"dimension_results":{"scope":"per_candidate","ranking":ranking},"explanations":[e for c in ranked for e in c["explanations"]],
        "data_gaps":gaps,"rejected_candidates":rejected,"limitations":data["limitations"],
        "provenance":{"knowledge_schema":data["schema_version"],"dataset_origin":data["origin"],"engine_version":"prototype.1",
            "release_inputs":data["release_inputs"],"environment_response_sha256":environment["response_sha256"],"input":request,
            "environmental_sources":space["provenance"] if space else None,
            "location_scope":"Bangladesh declared by user; coordinates are not independently jurisdiction-verified. National calendar and conditional coastal sequence applicability are retained as provisional."}}


def plan(request,provider,*,allow_fixtures=False,environmental_provider=None):
    mode=request.get("mode","prototype_recommendation")
    if mode=="prototype_recommendation":
        return prototype_plan(request,provider,environmental_provider)
    data=load_dataset(mode,allow_fixtures=allow_fixtures)
    location=request["location"];period=request["historical_period"]
    environment=provider.profile(location["latitude"],location["longitude"],period["start"],period["end"])
    crops={c["id"]:c for c in data["crops"]}
    assessments={c:assess_crop(crop,environment,request.get("soil",{})) for c,crop in crops.items()}
    gaps=[{"dimension":k,"status":"insufficient_data","message":"No approved local data/evaluation method"} for k in UNSUPPORTED]
    if not all(any(calendar_ready(cal) for cal in crop["calendars"]) for crop in crops.values()):
        gaps.append({"dimension":"calendar","status":"insufficient_data","message":"No verified local calendars. Provisional researcher dates are excluded from generation."})
    if not data.get("rotation_rules"):
        gaps.append({"dimension":"sequence_rules","status":"insufficient_data","message":"Local system evidence has not been activated as verified executable sequence rules."})
    if request.get("soil",{}).get("ph") is None:gaps.append({"dimension":"soil_suitability","status":"insufficient_data","message":"Soil pH unknown; no regional default applied."})
    candidates,rejected=generate(data,request)
    evaluated=[evaluate(c,crops,assessments,request) for c in candidates]
    ranked,ranking=rank(evaluated,request["priorities"])
    fixture=mode=="development_fixture"
    if not candidates:
        status="blocked_scientific_data" if any(g["dimension"] in ("calendar","sequence_rules") for g in gaps) else "no_feasible_rotation"
    else:status="development_fixture_results" if fixture else "candidate_rotations"
    return {"status":status,"mode":mode,"dataset_origin":data["origin"],"is_recommendation":False if fixture or not candidates else True,"notice":"DEVELOPMENT_FIXTURE: synthetic agronomy for pipeline testing only. Never use for farming." if fixture else "Historical global-species comparisons are reference context, not locally validated advice.","environment_profile":environment,"candidate_rotations":ranked,"crop_comparisons":list(assessments.values()),"dimension_results":{k:insufficient("No feasible verified calendar-backed candidates") for k in ("climate_suitability","soil_suitability","rotation_quality","farmer_priority_fit")} if not candidates else {"scope":"per_candidate","ranking":ranking},"ranking":ranking,"explanations":[e for c in ranked for e in c["explanations"]],"data_gaps":gaps,"rejected_candidates":rejected,"provenance":{"knowledge_schema":data["schema_version"],"dataset_origin":data["origin"],"engine_version":"milestone1.1","environment_response_sha256":environment["response_sha256"],"input":request},"limitations":data.get("limitations",[])}
