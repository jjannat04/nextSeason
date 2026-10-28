"""SMAP L4 v008 through AppEEARS point jobs, not the POWER API."""
import csv
from datetime import date, datetime, timedelta, timezone
import io
import json
import os
from pathlib import Path
import threading
import requests
from .cache import Cache, fetch, job_timed_out, number, now, unavailable
from .power import query_for

BASE = "https://appeears.earthdatacloud.nasa.gov/api"
PRODUCT = "SPL4SMGP.008"
LAYERS = {"surface_soil_moisture": "Geophysical_Data_sm_surface", "root_zone_soil_moisture": "Geophysical_Data_sm_rootzone", "root_zone_percentile": "Geophysical_Data_sm_rootzone_pctl"}
_LOCK = threading.Lock()


def parse_csv(content, query):
    rows = list(csv.DictReader(io.StringIO(content.decode("utf-8-sig"))))
    if not rows:
        raise ValueError("Empty SMAP point extraction")
    header = list(rows[0])
    columns = {}
    for name, layer in LAYERS.items():
        matches = [k for k in header if k in (f"SPL4SMGP_008_{layer}", layer)]
        if len(matches) != 1:
            raise ValueError("Unsupported SMAP CSV layer schema")
        columns[name] = matches[0]
    series = {k: [] for k in LAYERS}
    seen = set()
    for row in rows:
        latitude=number(row["Latitude"],minimum=-90,maximum=90)
        longitude=number(row["Longitude"],minimum=-180,maximum=180)
        if latitude is None or longitude is None or abs(latitude - query["latitude"]) > 1e-5 or abs(longitude - query["longitude"]) > 1e-5:
            raise ValueError("SMAP result point differs from request")
        stamp = row["Date"].strip()
        if len(stamp) == 10:
            if not row.get("Time"):
                raise ValueError("SMAP 3-hour timestamp absent; daily values cannot be assumed")
            stamp += "T" + row["Time"].strip()
        point = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        point = point.replace(tzinfo=timezone.utc) if point.tzinfo is None else point.astimezone(timezone.utc)
        if not query["start"] <= point.date().isoformat() <= query["end"]:
            raise ValueError("SMAP result outside requested period")
        iso = point.isoformat()
        if iso in seen:
            raise ValueError("Duplicate SMAP timestamp")
        seen.add(iso)
        for name, column in columns.items():
            series[name].append({"time": iso, "value": number(row[column], maximum=100 if name.endswith("percentile") else .9)})
    expected = ((date.fromisoformat(query["end"]) - date.fromisoformat(query["start"])).days + 1) * 8
    result = {}
    for name, points in series.items():
        points.sort(key=lambda p: p["time"])
        valid = [p["value"] for p in points if p["value"] is not None]
        times = [datetime.fromisoformat(p["time"]) for p in points]
        regular = len(times) == expected and all((b-a) == timedelta(hours=3) for a,b in zip(times,times[1:]))
        result[name] = {"unit": "percentile" if name.endswith("percentile") else "m3/m3", "points": points,
            "mean": sum(valid) / len(valid) if valid else None, "coverage": {"valid_samples": len(valid), "expected_samples": expected, "complete": len(valid) == expected and regular}}
    return result


class SmapProvider:
    def __init__(self, cache_dir, token=None, session=None):
        self.root = Path(cache_dir) / "smap"
        self.token = token if token is not None else os.environ.get("NASA_APPEEARS_TOKEN")
        self.session = session or requests.Session()
        self.harmony = None
        if token is None and not self.token:
            from .smap_harmony import SmapHarmonyProvider
            self.harmony = SmapHarmonyProvider(cache_dir, session=self.session)

    def profile(self, latitude, longitude, start, end):
        if self.harmony is not None:
            return self.harmony.profile(latitude, longitude, start, end)
        query_for(latitude, longitude, start, end)
        query = {"latitude": latitude, "longitude": longitude, "start": start, "end": end,
            "product": PRODUCT, "layers": LAYERS, "adapter_version": 1}
        cache = Cache(self.root, query)
        def missing(reason, state="unavailable", job=None):
            return unavailable("SMAP", PRODUCT, query, reason, access="AppEEARS asynchronous point extraction", resolution="9 km EASE-Grid 2.0", temporal="3-hourly", state=state, job_id=job)
        with _LOCK:
            saved = cache.read()
            if saved and saved.get("profile"):
                result = saved["profile"]
                result["cache_status"] = "cached"
                return result
            if not self.token:
                return missing("SMAP extraction requires a server-side AppEEARS token; none is configured.", "authentication_required")
            try:
                def get(path):
                    body, _ = fetch(self.session, "GET", BASE + path, token=self.token)
                    return json.loads(body)
                if not saved:
                    task = {"task_type": "point", "task_name": "next-season-" + cache.key[:16], "params": {
                        "dates": [{"startDate": date.fromisoformat(start).strftime("%m-%d-%Y"), "endDate": date.fromisoformat(end).strftime("%m-%d-%Y")}],
                        "layers": [{"product": PRODUCT, "layer": layer} for layer in LAYERS.values()],
                        "coordinates": [{"id": "farm", "latitude": latitude, "longitude": longitude}]}}
                    body, _ = fetch(self.session, "POST", BASE + "/task", token=self.token, json=task)
                    task_id = json.loads(body)["task_id"]
                    saved = {"task_id": task_id, "submitted_at": now(), "raw_objects": []}
                    cache.write(saved)
                    return missing("SMAP extraction submitted; values are unavailable while NASA processes the job.", "pending", task_id)
                task_id = saved["task_id"]
                task = get("/task/" + task_id)
                if task.get("status") != "done":
                    state = "failed" if task.get("status") in ("error", "failed") else "pending"
                    if state == "pending" and job_timed_out(saved.get("submitted_at")):
                        state = "job_timeout"
                    return missing("SMAP extraction is " + state + "; no observation values have been substituted.", state, task_id)
                bundle = get("/bundle/" + task_id)
                files = [f for f in bundle["files"] if PRODUCT.replace(".", "-") in f["file_name"] or "SPL4SMGP" in f["file_name"]]
                files = [f for f in files if f["file_name"].endswith(".csv") and "result" in f["file_name"].lower()]
                if len(files) != 1:
                    raise ValueError("Expected a single SMAP point-results CSV")
                file = files[0]
                url = BASE + "/bundle/" + task_id + "/" + file["file_id"]
                body, _ = fetch(self.session, "GET", url, token=self.token, download=True)
                raw = cache.raw(body, url)
                if raw["sha256"] != file["sha256"]:
                    raise ValueError("SMAP bundle checksum mismatch")
                series = parse_csv(body, query)
                observed=sorted({p["time"] for s in series.values() for p in s["points"] if p["value"] is not None})
                result = {"status": "available" if any(s["mean"] is not None for s in series.values()) else "unavailable", "provider": "SMAP", "product": PRODUCT,
                    "access_status":"ready" if observed else "no_valid_observations", "reason":None if observed else "No SMAP values passed the source fill/range checks.",
                    "location": {"latitude": latitude, "longitude": longitude}, "period": {"start": start, "end": end},
                    "observation_period":{"start":observed[0],"end":observed[-1]} if observed else None,
                    "spatial_resolution": "9 km EASE-Grid 2.0", "temporal_resolution": "3-hourly", "cache_status": "live_retrieved", "series": series,
                    "depths": {"surface_soil_moisture": "0–5 cm", "root_zone_soil_moisture": "0–100 cm"},
                    "provenance": {"product": PRODUCT, "collection_id": "C3480440870-NSIDC_CPRD", "access_method": "AppEEARS point extraction", "query": query,
                        "job_id": task_id, "retrieved_at": now(), "raw_objects": [raw], "source": "https://nsidc.org/data/spl4smgp/versions/8",
                        "variable_metadata": BASE + "/product/" + PRODUCT},
                    "limitations": ["Assimilated land-model estimates constrained by SMAP observations, not direct root-zone or field measurements.",
                        "Point sample on a 9 km grid; source pixel centre is not supplied by the CSV point coordinates.",
                        "Root-zone percentile resolves NASA's product seasonal climatology; fill percentiles remain unknown. Below median is not a calibrated crop-damage threshold."]}
                cache.write({**saved, "profile": result, "raw_objects": [raw]})
                return result
            except (requests.RequestException, ValueError, KeyError, TypeError, OSError):
                return missing("SMAP access, extraction schema or quality validation failed. Check authorized access and the saved NASA task; no values were substituted.", "access_or_data_error", (saved or {}).get("task_id"))
