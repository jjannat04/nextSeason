"""Categorical reference comparisons, not calibrated biological scores."""
from ..knowledge.repository import usable

USE="global_species_reference_comparison"
UNSUPPORTED=("water_resilience","soil_health_contribution","stage_stress","salinity_risk","income","low_input_cost")


def insufficient(reason):
    return {"status":"insufficient_data","value":None,"reason":reason,"evidence":[]}


def assess_crop(crop,environment,soil):
    temperature=crop["temperature"]
    required=("temp_optimal_min_c","temp_optimal_max_c","temp_absolute_min_c","temp_absolute_max_c")
    if not all(usable(temperature.get(k),USE) for k in required):
        climate=insufficient("Verified temperature reference unavailable")
    elif environment.get("status")!="available" or not environment["coverage"]["T2M"]["complete"]:
        climate=insufficient("Complete historical daily mean temperature series required")
    else:
        value=environment["series"]["T2M"]["mean"]
        lo,hi,absolute_lo,absolute_hi=[temperature[k]["normalized_value"] for k in required]
        category="within_optimal_reference" if lo<=value<=hi else "within_absolute_reference" if absolute_lo<=value<=absolute_hi else "outside_reference"
        climate={"status":"supported_reference_comparison","value":category,"period_mean_temperature_c":value,"evidence":[temperature[k] for k in required],"environment_source":{"provider":"NASA POWER","parameter":"T2M","period":environment["period"],"time_standard":environment["time_standard"],"response_sha256":environment["response_sha256"]},"limitation":"Comparison of the historical period mean to a global-species envelope; not local/stage suitability or future weather"}
    ph=soil.get("ph")
    fields=crop["soil_ph"]
    if ph is None:
        soil_result=insufficient("Farmer soil pH is unknown")
    elif not all(usable(fields.get(k),USE) for k in ("soil_ph_opt_min","soil_ph_opt_max")):
        soil_result=insufficient("Verified soil pH reference unavailable")
    else:
        lo=fields["soil_ph_opt_min"]["normalized_value"];hi=fields["soil_ph_opt_max"]["normalized_value"]
        soil_result={"status":"supported_reference_comparison","value":"within_optimal_reference" if lo<=ph<=hi else "outside_optimal_reference","farmer_value":ph,"measurement_method":soil.get("ph_method","unspecified"),"evidence":list(fields.values()),"limitation":"Outside optimum does not mean impossible; test-method/local applicability not calibrated"}
    return {"crop_id":crop["id"],"label":crop["label"],"climate_suitability":climate,"soil_suitability":soil_result,**{k:insufficient("No approved calibrated or qualitative evaluation rule for this dimension") for k in UNSUPPORTED}}


def evaluate(candidate,crops,assessments,request):
    ids=[a["crop_id"] for a in candidate["activities"]]
    dimensions={}
    for key in ("climate_suitability","soil_suitability"):
        components=[assessments[c][key] for c in ids]
        if any(c["status"]=="insufficient_data" for c in components):
            dimensions[key]=insufficient("One or more crop comparisons are unavailable")
        else:
            order={"within_optimal_reference":0,"within_absolute_reference":1,"outside_optimal_reference":1,"outside_reference":2}
            worst=max((c["value"] for c in components),key=lambda c:order[c])
            dimensions[key]={"status":"supported_reference_comparison","value":worst,"components":components,"evidence":[e for c in components for e in c["evidence"]]}
    if all(usable(crops[c].get("family_evidence"),"structural_comparison") for c in ids):
        families={crops[c]["family"] for c in ids}
        dimensions["rotation_quality"]={"status":"structural_proxy","value":len(families),"metric":"distinct_crop_families","limitation":"Family count is not measured soil improvement or disease protection","evidence":[crops[c]["family_evidence"] for c in ids]+candidate["sequence_evidence"]}
    else:
        dimensions["rotation_quality"]=insufficient("Crop family assertions have not been activated for structural comparison")
    preferred=set(request.get("preferred_crop_ids",[]))
    dimensions["farmer_priority_fit"]={"status":"farmer_preference","value":sum(c in preferred for c in ids),"metric":"preferred_crop_occurrences","preferred_crop_ids":sorted(preferred),"evidence":[{"source":"farmer_input","value":sorted(preferred)}]}
    dimensions.update({k:insufficient("No approved evaluation rule/data") for k in UNSUPPORTED})
    candidate["dimension_results"]=dimensions
    candidate["explanations"]=[{"claim":f"{key}: {result['value']}","dimension":key,"agronomic_evidence":result.get("evidence",[]),"environment_source":[component["environment_source"] for component in result.get("components",[]) if "environment_source" in component],"limitation":result.get("limitation")} for key,result in dimensions.items() if result["status"]!="insufficient_data"]
    return candidate
