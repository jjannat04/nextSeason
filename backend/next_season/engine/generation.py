"""Small exhaustive dated sequence search, using only activated records."""
from datetime import date,timedelta
from ..knowledge.repository import usable
from .constraints import check_plan

CALENDAR_FIELDS=("planting_start","planting_end","duration_days","turnaround_days")


def calendar_ready(record):
    return record.get("verification")=="verified" and all(usable(record.get("fields",{}).get(k),"rotation_feasibility") for k in CALENDAR_FIELDS)


def generate(dataset,request):
    crops={c["id"]:c for c in dataset["crops"]}
    rules={(r["previous"],r["next"]):r for r in dataset.get("rotation_rules",[]) if r.get("verification")=="verified" and "rotation_feasibility" in r.get("allowed_uses",[])}
    horizon=request.get("horizon",3)
    current=request.get("current_crop")
    previous=(current or {}).get("crop_id") or (request.get("crop_history") or [None])[-1]
    occupied=date.fromisoformat(current["harvest_date"]) if current else None
    candidates=[];rejected=[]
    def visit(activities,prev,end,trace):
        if len(activities)==horizon:
            checks=check_plan(activities,request)
            if any(c["status"]=="violated" for c in checks):
                rejected.append({"crop_ids":[a["crop_id"] for a in activities],"checks":checks});return
            candidates.append({"id":"rotation-"+"-".join(a["crop_id"] for a in activities),"activities":activities,"hard_constraints":checks,"sequence_evidence":trace})
            return
        for crop in crops.values():
            if crop["id"] in request.get("constraints",{}).get("excluded_crop_ids",[]):continue
            rule=rules.get((prev,crop["id"])) if prev else None
            if prev and not rule:continue
            for calendar in crop["calendars"]:
                if calendar.get("slot")!=len(activities) or not calendar_ready(calendar):continue
                fields=calendar["fields"]
                first=date.fromisoformat(fields["planting_start"]["normalized_value"])
                last=date.fromisoformat(fields["planting_end"]["normalized_value"])
                turnaround=fields["turnaround_days"]["normalized_value"]
                duration=fields["duration_days"]["normalized_value"]
                if not isinstance(duration,int) or duration<=0 or not isinstance(turnaround,int) or turnaround<1:continue
                planting=max(first,end+timedelta(days=turnaround)) if end else first
                earliest=request.get("constraints",{}).get("earliest_planting")
                if earliest:planting=max(planting,date.fromisoformat(earliest))
                if planting>last or planting<=date.today():continue
                harvest=planting+timedelta(days=duration)
                activity={"crop_id":crop["id"],"label":crop["label"],"planting":planting.isoformat(),"harvest":harvest.isoformat(),"calendar_id":calendar["id"],"calendar_evidence":fields,"sequence_rule_id":rule["id"] if rule else None}
                visit(activities+[activity],crop["id"],harvest,trace+([rule] if rule else []))
    visit([],previous,occupied,[])
    return candidates,rejected
