"""Priority-ordered comparison of separate dimensions. No overall score.

Farmer weight magnitudes establish dimension precedence, not scientific utility.
Equal weights break ties by documented dimension name. No hidden weighted sum.
"""
ORDER={"good_fit":0,"acceptable":1,"potential_concern":2,"within_optimal_reference":0,"within_absolute_reference":1,"outside_optimal_reference":1,"outside_reference":2}
PRIORITIES={"climate_suitability":"climate_suitability","soil_suitability":"soil_suitability","rotation_quality":"rotation_quality","preferred_crops":"farmer_priority_fit","water_conservation":"water_resilience","soil_health":"soil_health_contribution","income":"income","low_input_cost":"low_input_cost"}
PRIORITIES.update(rainfall_suitability="rainfall_suitability",moisture_context="historical_moisture_context")


def rank(candidates,priorities,*,allow_partial=False):
    if not candidates:
        return [],{"status":"no_candidates","unavailable_priorities":[],"method":"No verified feasible candidates; ranking has not run"}
    ordered=sorted(((k,v) for k,v in priorities.items() if v>0),key=lambda pair:(-pair[1],pair[0]))
    unavailable=[];supported=[]
    for key,_ in ordered:
        dimension=PRIORITIES[key]
        if any(c["dimension_results"].get(dimension,{}).get("status","insufficient_data")=="insufficient_data" for c in candidates):unavailable.append(key)
        else:supported.append((key,dimension))
    if unavailable and not allow_partial or not supported:
        # Preserve farmer preferences. Do not silently discard unavailable goals.
        return sorted(candidates,key=lambda c:c["id"]),{"status":"insufficient_data","unavailable_priorities":unavailable,"method":"No preference ranking produced; listed by stable ID"}
    def key(candidate):
        values=[]
        for _,dimension in supported:
            result=candidate["dimension_results"][dimension]
            value=result.get("ranking_value",result["value"])
            values.append(ORDER[value] if isinstance(value,str) else value if result.get("comparison_direction")=="lower_is_preferred" else -value)
        return tuple(values)
    candidates=sorted(candidates,key=lambda c:(key(c),c["id"]))
    previous=None;display_rank=0
    for index,c in enumerate(candidates,1):
        values=key(c)
        if values!=previous:display_rank=index
        c["rank"]=display_rank;c["ranking_comparison"]=list(values);previous=values
    return candidates,{"status":"partial_ranking" if unavailable else "ranked","unavailable_priorities":unavailable,"method":"Priority-ordered lexicographic comparison of supported dimensions; no overall score. Unavailable active goals remain explicitly unmet." if unavailable else "Priority-ordered lexicographic comparison; no overall score","priority_order":[key for key,_ in supported],"tie_break":"Equal priority weights sorted by name; equal dimension values share rank, stable ID display order"}
