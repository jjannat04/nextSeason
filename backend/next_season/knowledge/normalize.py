"""Offline staging only. Runtime never reads researcher CSVs.

Run: python -m next_season.knowledge.normalize (PYTHONPATH=backend).
All fields preserve raw values; only explicitly source-checked fields gain an
allowlisted reference-comparison use, never blanket production readiness.
"""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode

from .identity import ROOT, SLICE
from .schema import normalize_value

# Independently checked against the four official FAO EcoCrop Ecology tables,
# 2026-10-28. These are source-transcription checks, NOT local crop validation.
CHECKED = {
    "C01": {"temp_absolute_min_c":10,"temp_optimal_min_c":20,"temp_optimal_max_c":30,"temp_absolute_max_c":36,"soil_ph_opt_min":5.5,"soil_ph_opt_max":7},
    "C04": {"temp_absolute_min_c":10,"temp_optimal_min_c":18,"temp_optimal_max_c":33,"temp_absolute_max_c":47,"soil_ph_opt_min":5,"soil_ph_opt_max":7},
    "C05": {"temp_absolute_min_c":5,"temp_optimal_min_c":17,"temp_optimal_max_c":34,"temp_absolute_max_c":45,"soil_ph_opt_min":6,"soil_ph_opt_max":7.5},
    "C06": {"temp_absolute_min_c":8,"temp_optimal_min_c":21,"temp_optimal_max_c":36,"temp_absolute_max_c":40,"soil_ph_opt_min":5.5,"soil_ph_opt_max":6.2},
}
CHECKED_URLS={key:f"https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id={value}" for key,value in {"C01":1574,"C04":238663,"C05":1191,"C06":2150}.items()}
NUMERIC = set("typical_duration_days_min typical_duration_days_max soil_ph_opt_min soil_ph_opt_max planting_start_month planting_start_day planting_end_month planting_end_day harvest_start_month harvest_start_day harvest_end_month harvest_end_day typical_duration_days temp_absolute_min_c temp_optimal_min_c temp_optimal_max_c temp_absolute_max_c rainfall_min_mm rainfall_optimal_min_mm rainfall_optimal_max_mm rainfall_max_mm critical_heat_temp_c humidity_min_pct humidity_optimal_min_pct humidity_optimal_max_pct humidity_max_pct stage_start_fraction stage_end_fraction kc_value water_requirement_mm_min water_requirement_mm_typical water_requirement_mm_max kc_min kc_max ph_absolute_min ph_optimal_min ph_optimal_max ph_absolute_max salinity_threshold_ece_ds_m ece_threshold_ds_m yield_loss_pct_per_ds_m threshold_min threshold_max region_area_ha region_area_pct regional_soil_ph_min regional_soil_ph_max regional_salinity_ece_dsm observed_ph_min observed_ph_max observed_sample_n minimum_value maximum_value default_weight minimum_weight maximum_weight reported_value latitude longitude".split())
BOOLEANS = set("is_legume is_cereal is_oilseed is_pulse is_vegetable is_root_tuber nitrogen_fixing same_crop_family same_crop_species calendar_verification_required required".split())
UNIT = {**{k:"degC" for k in NUMERIC if k.startswith("temp_") or k=="critical_heat_temp_c"}, **{k:"mm/year" for k in NUMERIC if k.startswith("rainfall_")}, **{k:"fraction" for k in ("stage_start_fraction","stage_end_fraction")}, **{k:"dimensionless_Kc" for k in ("kc_value","kc_min","kc_max")}, **{k:"pH_method_unspecified" for k in NUMERIC if "ph_" in k}, **{k:"dS/m_ECe" for k in ("salinity_threshold_ece_ds_m","ece_threshold_ds_m")}}
UNIT.update({"yield_loss_pct_per_ds_m":"percentage_points_relative_yield_per_dS/m","water_requirement_mm_min":"mm_period_unspecified","water_requirement_mm_typical":"mm_period_unspecified","water_requirement_mm_max":"mm_period_unspecified","region_area_ha":"ha","region_area_pct":"percent","observed_sample_n":"count"})
UNIT_ALIASES={"dS_per_m":"dS/m","m3/ha":"m3/ha_period_unspecified","person_days_per_year":"person-days/year_area_unspecified","t/ha":"t/ha","percent":"percent","ratio":"dimensionless_ratio"}


def source_urls(raw):
    urls=[]
    for value in re.findall(r"https?://[^\s|]+",raw or ""):
        value=value.rstrip(",")
        parts=urlsplit(value)
        query=[(k,v) for k,v in parse_qsl(parts.query,keep_blank_values=True) if not k.lower().startswith("utm_")]
        urls.append(urlunsplit((parts.scheme,parts.netloc,parts.path,urlencode(query),parts.fragment)))
    return list(dict.fromkeys(urls))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def build(root=ROOT):
    root = Path(root)
    spec = json.loads((root/"data/crosswalk/spec.json").read_text(encoding="utf-8"))
    aliases = {}
    unresolved = []
    def add(namespace, raw, canonical, cultivar=None, kind="crop"):
        key = (namespace, raw)
        entry = {"namespace":namespace,"raw":raw,"canonical_id":canonical,"variety_id":cultivar,"kind":kind,"status":"mapped"}
        if key in aliases and aliases[key] != entry:
            raise ValueError(f"Ambiguous crosswalk: {key}")
        aliases[key] = entry
        return entry
    # Explicit namespaces also allow review of registry numeric values.
    def identify(raw, filename):
        if raw in spec["master"]:
            return add(filename,raw,spec["master"][raw])
        if raw in spec["legacy"]:
            _,crop,variety=spec["legacy"][raw]
            return add(filename,raw,crop,variety)
        for slug,crop,variety in spec["legacy"].values():
            if raw==slug:
                return add(filename,raw,crop,variety)
        if raw in spec["names"]:
            return add(filename,raw,spec["names"][raw])
        canonical_names=set(spec["master"].values())|set(spec["names"].values())
        if raw in canonical_names:
            return add(filename,raw,raw)
        if raw in spec["scientific_names"]:
            return add(filename,raw,spec["scientific_names"][raw])
        if raw in spec["activities"]:
            return add(filename,raw,None,kind="land_use_activity")
        return None
    records=[];manifest=[];conflicts=[];errors=[];crop_data={}
    for path in sorted((root/"research/csv").glob("*.csv"), key=lambda p:int(p.name.split("_")[0])):
        file_no=int(path.name.split("_")[0]);sha=digest(path)
        with path.open(encoding="utf-8-sig",newline="") as f:
            rows=list(csv.DictReader(f))
        manifest.append({"file":path.name,"sha256":sha,"rows":len(rows)})
        for index,row in enumerate(rows,2):
            if None in row or any(v is None for v in row.values()):
                raise ValueError(f"Malformed CSV record {path.name}:{index}")
            record_id=f"{path.name}:{index}"
            subject=identify(row.get("crop_id",""),path.name) if "crop_id" in row else None
            refs={}
            for key in ("crop_id","crop_name","crop_name_en","scientific_name","previous_crop_id","next_crop_id"):
                if key in row and normalize_value(row[key]) is not None:
                    mapping=identify(row[key],path.name)
                    if mapping:refs[key]=mapping
                    else:unresolved.append({"record":record_id,"column":key,"raw":row[key],"reason":spec["ambiguous"].get(row[key],"No explicit mapping; human review required")})
            if normalize_value(row.get("variety","")) is not None:
                raw=row["variety"]
                # Varieties in files 9/11 already have an explicit crop/system column.
                if subject and re.fullmatch(r"BRRI_dhan\d+",raw):
                    refs["variety"]=add(path.name,raw,subject["canonical_id"],raw.lower())
                else:unresolved.append({"record":record_id,"column":"variety","raw":raw,"reason":"Unmapped cultivar"})
            for key in ("candidate_sequence","current_rotation","previous_crop_1","previous_crop_2","crops_covered"):
                if normalize_value(row.get(key,"")) is None:continue
                # Preserve overlap and landscape text independently of identified tokens.
                text=row[key]
                if key=="crops_covered":tokens=[t.strip() for t in text.split("|")]
                elif text.startswith("Boro area replaced"):
                    tokens=["Boro rice","Aus rice"]+(["Rabi crops"] if "Rabi crops" in text else [])
                else:tokens=[t.strip().removesuffix(" relay") for t in re.split(r">|/",text)]
                refs[key]=[]
                for token in tokens:
                    mapping=identify(token,path.name)
                    if mapping:refs[key].append(mapping)
                    else:unresolved.append({"record":record_id,"column":key,"raw":token,"reason":spec["ambiguous"].get(token,"No explicit mapping; human review required")})
            source={"source_title":row.get("source_title",row.get("title")),"source_url":row.get("source_url",row.get("url")),"source_year":row.get("source_year",row.get("year"))}
            source["normalized_urls"]=source_urls(source["source_url"])
            scope=row.get("source_scope",row.get("dataset_scope",row.get("region_scope",row.get("geographic_applicability",row.get("applicability",row.get("assessment_scope"))))))
            fields={}
            for column,raw in row.items():
                kind="number" if column in NUMERIC else "boolean" if column in BOOLEANS else "text"
                try:value=normalize_value(raw,kind)
                except ValueError as exc:
                    errors.append({"record":record_id,"column":column,"error":str(exc)});value=None
                if column in ("unit","reported_unit","threshold_unit") and value is not None:
                    value=UNIT_ALIASES.get(value,value)
                if column in ("crop_id","previous_crop_id","next_crop_id") and column in refs:
                    value=refs[column]["canonical_id"]
                if column=="variety" and column in refs:
                    value=refs[column]["variety_id"]
                field={"raw_value":raw,"normalized_value":value,"verification":"missing" if value is None else "provisional","source":dict(source),"confidence":row.get("confidence_level",row.get("evidence_strength")),"notes":row.get("notes"),"geographic_applicability":scope,"provenance":{"file":path.name,"record":index,"column":column,"sha256":sha},"unit":UNIT.get(column),"allowed_uses":[]}
                if value is None:field["missing_reason"]="unspecified_missing"
                if column in refs and isinstance(refs[column],dict):
                    field["identity_mapping"]={"canonical_id":refs[column]["canonical_id"],"variety_id":refs[column]["variety_id"],"namespace":path.name,"meaning":"Identity mapping only; scientific applicability remains separately gated"}
                if column in ("threshold_min","threshold_max"):
                    field["unit"]=UNIT_ALIASES.get(row.get("threshold_unit"),row.get("threshold_unit")) if normalize_value(row.get("threshold_unit","")) is not None else None
                if column=="reported_value":field["unit"]=UNIT_ALIASES.get(row.get("reported_unit"),row.get("reported_unit"))
                if file_no in (1,3) and row.get("crop_id") in CHECKED and column in CHECKED[row["crop_id"]]:
                    # File-specific fields are independently checked, not inherited from row readiness.
                    if value!=CHECKED[row["crop_id"]][column] or source["source_url"]!=CHECKED_URLS[row["crop_id"]]:raise ValueError(f"Source-check mismatch: {record_id}/{column}")
                    field.update(verification="verified",allowed_uses=["global_species_reference_comparison"],geographic_applicability="global_species_reference")
                    field["review"]={"method":"official_source_transcription_check","date":"2026-10-28","locator":"Ecology: Temperature requirements" if column.startswith("temp_") else "Ecology: Soil PH (Optimal)","limitation":"Not local calendar, cultivar or crop-stage validation"}
                if file_no==5 and column=="salinity_threshold_ece_ds_m" and row["crop_id"] in ("1","9","11"):
                    field["verification"]="conflicting"
                    conflicts.append({"id":f"salinity-{row['crop_id']}","claim":field,"other_record":f"7_crop_salinity_response.csv:{int(row['crop_id'])+1}","reason":"Observation/stage descriptor is not a verified yield-loss threshold; preserve both records","resolution":None})
                fields[column]=field
            record={"id":record_id,"raw":row,"fields":fields,"subject":subject,"crop_references":refs}
            records.append(record)
            if subject and subject["canonical_id"] in SLICE:
                crop=crop_data.setdefault(subject["canonical_id"],{"id":subject["canonical_id"],"label":subject["canonical_id"].replace("_"," ").title(),"family":None,"temperature":{},"soil_ph":{},"calendars":[],"origin":"RESEARCH_EVIDENCE"})
                if file_no==1:
                    crop["label"]=row["crop_name_en"];crop["family"]=row["crop_family"];crop["family_evidence"]=fields["crop_family"]
                    crop["soil_ph"]={k:fields[k] for k in ("soil_ph_opt_min","soil_ph_opt_max")}
                if file_no==3:crop["temperature"]={k:fields[k] for k in CHECKED[row["crop_id"]] if k.startswith("temp_")}
                if file_no==2:crop["calendars"].append({"id":record_id,"fields":fields,"verification":"provisional"})
    if errors:raise ValueError(f"Normalization errors; no release written: {errors}")
    # Missing mapping is a reported research issue, never an auto-created crop.
    write(root/"data/crosswalk/crops.json",{"schema_version":1,"aliases":list(aliases.values()),"unresolved":unresolved})
    output=root/"data/normalized"
    write(output/"staging.json",{"schema_version":1,"origin":"RESEARCH_STAGING_NOT_FOR_SCORING","records":records})
    write(output/"manifest.json",{"schema_version":1,"assets":manifest,"records":len(records)})
    write(output/"conflicts.json",{"conflicts":conflicts,"policy":"No automatic reconciliation; all claims retained in staging.json"})
    release={"schema_version":1,"origin":"RESEARCH_EVIDENCE","status":"calendar_blocked","allowed_use":"global_species_reference_comparison","crops":[crop_data[c] for c in SLICE],"rotation_rules":[],"limitations":["No verified local calendars or executable sequence rules", "No calibrated water, salinity, stage-stress, soil-health or economic scores"]}
    write(output/"slice.json",release)
    for asset in manifest:
        if digest(root/"research/csv"/asset["file"])!=asset["sha256"]:raise ValueError("Raw research changed during normalization")
    return {"records":len(records),"aliases":len(aliases),"unresolved":len(unresolved),"conflicts":len(conflicts)}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(json.dumps(build()))
