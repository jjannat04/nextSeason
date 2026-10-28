"""Farmer requirements are a separate binary ledger, never ranking weights."""
from datetime import date


def check_plan(activities,request):
    limits=request.get("constraints",{})
    ids=[a["crop_id"] for a in activities]
    checks=[]
    def start(activity):
        if "planting_window" in activity:
            return date.fromisoformat(activity["planting_window"]["start"]+"-01")
        return date.fromisoformat(activity["planting"])
    def end(activity):
        if "harvest_window" in activity:
            from .month_generation import month_end
            return month_end(activity["harvest_window"]["end"])
        return date.fromisoformat(activity["harvest"])
    def check(name,passes,detail):
        checks.append({"constraint":name,"status":"satisfied" if passes else "violated","detail":detail})
    check("excluded_crops",not set(ids)&set(limits.get("excluded_crop_ids",[])),"Excluded crops cannot appear")
    check("required_crops",set(limits.get("required_crop_ids",[]))<=set(ids),"Every required crop must remain")
    for slot,crop in limits.get("locked_slots",{}).items():
        check(f"locked_slot_{slot}",int(slot)<len(ids) and ids[int(slot)]==crop,"Farmer locked this slot")
    baseline=limits.get("baseline",[])
    if limits.get("max_changes") is not None:
        check("max_changes",len(baseline)==len(ids) and sum(a!=b for a,b in zip(ids,baseline))<=limits["max_changes"],"Compared with farmer's slot-by-slot baseline")
    for previous,next_ in zip(activities,activities[1:]):
        check("no_planting_overlap",end(previous)<start(next_),"Latest harvest envelope precedes earliest next planting envelope")
    if limits.get("earliest_planting"):
        check("earliest_planting",all(start(a)>=date.fromisoformat(limits["earliest_planting"]) for a in activities),"Farmer planting deadline; whole-month bounds used conservatively")
    if limits.get("latest_harvest"):
        check("latest_harvest",all(end(a)<=date.fromisoformat(limits["latest_harvest"]) for a in activities),"Farmer harvest deadline; whole-month bounds used conservatively")
    return checks
