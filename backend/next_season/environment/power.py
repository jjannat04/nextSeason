"""NASA POWER daily point adapter with exact-query, checked raw-response cache."""
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import os
import tempfile
import requests

URL="https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMETERS=("T2M","T2M_MIN","T2M_MAX","PRECTOTCORR")


class PowerError(RuntimeError):
    pass


def checksum(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,allow_nan=False).encode()).hexdigest()


def days(start,end):
    start=date.fromisoformat(start);end=date.fromisoformat(end)
    return [(start+timedelta(days=i)).strftime("%Y%m%d") for i in range((end-start).days+1)]


def query_for(latitude,longitude,start,end):
    if not math.isfinite(latitude) or not -90<=latitude<=90 or not math.isfinite(longitude) or not -180<=longitude<=180:
        raise ValueError("Invalid coordinates")
    first=date.fromisoformat(start);last=date.fromisoformat(end)
    if not 0<=(last-first).days<=365 or last>=date.today():
        raise ValueError("Choose a past historical period of at most 366 days")
    return {"latitude":latitude,"longitude":longitude,"start":first.strftime("%Y%m%d"),"end":last.strftime("%Y%m%d"),"parameters":",".join(PARAMETERS),"community":"AG","format":"JSON","time-standard":"UTC"}


def normalize(payload,query,*,retrieved_at,cache_status):
    try:
        series=payload["properties"]["parameter"]
        metadata=payload["parameters"]
        start=datetime.strptime(query["start"],"%Y%m%d").date().isoformat()
        end=datetime.strptime(query["end"],"%Y%m%d").date().isoformat()
        expected=days(start,end)
        fill=payload.get("header",{}).get("fill_value",-999)
        normalized={};coverage={}
        for parameter in PARAMETERS:
            if parameter not in series or parameter not in metadata:
                raise PowerError(f"Missing POWER parameter {parameter}")
            raw_unit=metadata[parameter].get("units")
            valid_units=("C","degC","°C") if parameter!="PRECTOTCORR" else ("mm/day", "mm/d")
            if raw_unit not in valid_units:
                raise PowerError(f"Unexpected {parameter} unit: {raw_unit}")
            values=[]
            for key in expected:
                raw=series[parameter].get(key)
                if raw is None or raw==fill or raw==-999:
                    value=None
                elif not isinstance(raw,(float,int)) or isinstance(raw,bool) or not math.isfinite(raw):
                    raise PowerError("Non-numeric POWER observation")
                elif parameter=="PRECTOTCORR" and raw<0:
                    value=None
                else:value=raw
                values.append({"date":datetime.strptime(key,"%Y%m%d").date().isoformat(),"value":value})
            valid=[v["value"] for v in values if v["value"] is not None]
            normalized[parameter]={"unit":"degC" if parameter!="PRECTOTCORR" else "mm/day","source_unit":raw_unit,"daily":values,"mean":sum(valid)/len(valid) if valid else None,"total":sum(valid) if valid and parameter=="PRECTOTCORR" else None}
            coverage[parameter]={"valid_days":len(valid),"expected_days":len(expected),"complete":len(valid)==len(expected)}
        return {"status":"available","provider":"NASA POWER","profile_type":"historical_observations_not_forecast","location":{"latitude":query["latitude"],"longitude":query["longitude"]},"period":{"start":start,"end":end},"time_standard":"UTC","retrieved_at":retrieved_at,"cache_status":cache_status,"query":query,"request_url":URL,"response_sha256":checksum(payload),"source_metadata":{"header":payload.get("header",{}),"geometry":payload.get("geometry"),"parameters":metadata},"coverage":coverage,"series":normalized,"limitations":["Regional gridded data, not a field measurement","Period mean comparison is not crop-stage stress or a forecast","Rainfall is not irrigation requirement"]}
    except (KeyError,TypeError,ValueError) as exc:
        raise PowerError("Invalid POWER response structure") from exc


class PowerProvider:
    def __init__(self,cache_dir,session=None):
        self.cache_dir=Path(cache_dir)
        self.session=session or requests.Session()

    def profile(self,latitude,longitude,start,end):
        query=query_for(latitude,longitude,start,end)
        path=self.cache_dir/(checksum({"adapter_version":1,"query":query})+".json")
        if path.exists():
            try:
                cached=json.loads(path.read_text(encoding="utf-8"))
                retrieved=datetime.fromisoformat(cached["retrieved_at"])
                recent=date.fromisoformat(end)>date.today()-timedelta(days=30)
                fresh=not recent or datetime.now(timezone.utc)-retrieved<timedelta(days=7)
                if cached["query"]==query and checksum(cached["raw_response"])==cached["response_sha256"] and fresh:
                    return normalize(cached["raw_response"],query,retrieved_at=cached["retrieved_at"],cache_status="cached")
            except (ValueError,KeyError,TypeError,PowerError):pass
        try:
            response=self.session.get(URL,params=query,timeout=(5,25))
            response.raise_for_status()
            payload=response.json()
        except (requests.RequestException,ValueError) as exc:
            raise PowerError("NASA POWER unavailable; no valid matching cache. Try again later.") from exc
        timestamp=datetime.now(timezone.utc).isoformat()
        profile=normalize(payload,query,retrieved_at=timestamp,cache_status="live_retrieved")
        self.cache_dir.mkdir(parents=True,exist_ok=True)
        # Atomic replacement prevents half-written cache entries across requests.
        fd,temp=tempfile.mkstemp(dir=self.cache_dir,suffix=".tmp")
        try:
            with os.fdopen(fd,"w",encoding="utf-8") as f:
                json.dump({"query":query,"retrieved_at":timestamp,"response_sha256":profile["response_sha256"],"raw_response":payload},f,allow_nan=False)
            os.replace(temp,path)
        finally:
            if os.path.exists(temp):os.unlink(temp)
        return profile
