"""IMERG Final V07: Harmony geographic subsets, then native NetCDF decoding."""
from datetime import date, timedelta
import json
import math
import os
from pathlib import Path
import threading
from urllib.parse import urljoin
import requests
from .cache import Cache, fetch, job_timed_out, number, now, public_url, unavailable
from .power import query_for

PRODUCT = "GPM_3IMERGDF.07"
COLLECTION = "C2723754864-GES_DISC"
BASE = "https://harmony.earthdata.nasa.gov"
_LOCK = threading.Lock()  # NetCDF/HDF5 library is not assumed thread-safe.


def parse_netcdf(content, query):
    import netCDF4
    import numpy as np
    with netCDF4.Dataset("imerg-point-subset", memory=content) as dataset:
        if getattr(dataset, "DOI", "") != "10.5067/GPM/IMERGDF/DAY/07" or "GPM IMERG Final Precipitation L3 1 day" not in getattr(dataset, "title", ""):
            raise ValueError("IMERG Final V07 native product identity mismatch")
        source_start, source_end = getattr(dataset, "BeginDate", None), getattr(dataset, "EndDate", None)
        if not source_start or not source_end or source_start > source_end:
            raise ValueError("IMERG source observation period unavailable")
        variables = dataset.variables
        rain, count = variables["precipitation"], variables["precipitation_cnt"]
        if getattr(rain, "units", "") not in ("mm/day", "mm day-1", "mm d-1"):
            raise ValueError("IMERG daily rate has unexpected units")
        if getattr(count, "units", "") not in ("count", "counts", "1"):
            raise ValueError("IMERG retrieval count has unexpected units")
        lat, lon, time = variables["lat"], variables["lon"], variables["time"]
        if lat.ndim != 1 or lon.ndim != 1 or time.ndim != 1:
            raise ValueError("Unsupported IMERG coordinate schema")
        if not np.isfinite(lat[:]).all() or not np.isfinite(lon[:]).all():
            raise ValueError("IMERG coordinates are not finite")
        if getattr(lat, "units", "") not in ("degrees_north", "degrees") or getattr(lon, "units", "") not in ("degrees_east", "degrees"):
            raise ValueError("IMERG coordinate units unavailable")
        lat_index = int(np.argmin(abs(lat[:] - query["latitude"])))
        lon_index = int(np.argmin(abs(lon[:] - query["longitude"])))
        cell = {"latitude": float(lat[lat_index]), "longitude": float(lon[lon_index])}
        if abs(cell["latitude"] - query["latitude"]) > .1001 or abs(cell["longitude"] - query["longitude"]) > .1001:
            raise ValueError("IMERG returned grid is not near the requested point")
        lat_dim, lon_dim, time_dim = lat.dimensions[0], lon.dimensions[0], time.dimensions[0]
        points = []
        def scalar(variable, t):
            indices = {lat_dim: lat_index, lon_dim: lon_index, time_dim: t}
            if any(dim not in indices for dim in variable.dimensions):
                raise ValueError("Unsupported IMERG variable dimensions")
            value = variable[tuple(indices[d] for d in variable.dimensions)]
            return None if np.ma.is_masked(value) else float(value)
        for t, stamp in enumerate(netCDF4.num2date(time[:], time.units, calendar=getattr(time, "calendar", "standard"))):
            day = f"{stamp.year:04}-{stamp.month:02}-{stamp.day:02}"
            if not query["start"] <= day <= query["end"]:
                raise ValueError("IMERG time outside requested interval")
            if not source_start <= day <= source_end:
                raise ValueError("IMERG native source dates disagree with time axis")
            n = number(scalar(count, t), maximum=48)
            value = number(scalar(rain, t)) if n == 48 else None
            points.append({"date": day, "value": value, "valid_half_hour_samples": n, "sampled_grid": cell,
                           "source_doi": dataset.DOI, "source_observation_period": {"start": source_start, "end": source_end},
                           "source_production_time": getattr(dataset, "ProductionTime", None)})
        return points


def summarize(points, start, end):
    by_date = {}
    for point in points:
        if point["date"] in by_date:
            raise ValueError("Duplicate/conflicting IMERG daily granule")
        by_date[point["date"]] = point
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    days = [(first + timedelta(days=i)).isoformat() for i in range((last-first).days+1)]
    daily = [by_date.get(d, {"date": d, "value": None, "valid_half_hour_samples": None}) for d in days]
    valid = [p["value"] for p in daily if p["value"] is not None]
    complete = len(valid) == len(days)
    return {"unit": "mm/day", "daily": daily, "mean": sum(valid)/len(valid) if valid else None,
        "total_mm": math.fsum(valid) if complete else None, "coverage": {"valid_days": len(valid), "expected_days": len(days), "complete": complete}}


class GpmProvider:
    def __init__(self, cache_dir, token=None, session=None):
        self.root = Path(cache_dir) / "gpm"
        self.token = token if token is not None else (os.environ.get("EARTHDATA_TOKEN") or os.environ.get("NASA_EARTHDATA_TOKEN"))
        self.session = session or requests.Session()

    def profile(self, latitude, longitude, start, end):
        query_for(latitude, longitude, start, end)
        query = {"latitude": latitude, "longitude": longitude, "start": start, "end": end,
            "product": PRODUCT, "collection_id": COLLECTION, "variables": ["precipitation", "precipitation_cnt", "lat", "lon", "time"], "adapter_version": 1}
        cache = Cache(self.root, query)
        def missing(reason, state="unavailable", job=None):
            return unavailable("GPM IMERG", PRODUCT, query, reason, access="Harmony asynchronous geographic subset / NetCDF", resolution="0.1° latitude × 0.1° longitude", temporal="daily (UTC); derived from half-hourly retrievals", state=state, job_id=job)
        with _LOCK:
            saved = cache.read()
            if saved and saved.get("profile"):
                result = saved["profile"]; result["cache_status"] = "cached"
                return result
            if not self.token:
                return missing("IMERG Final extraction requires a server-side Earthdata bearer token; none is configured.", "authentication_required")
            try:
                def get(url, **kwargs):
                    body, response = fetch(self.session, "GET", url, token=self.token, **kwargs)
                    return json.loads(body), response
                if not saved:
                    # Include coordinates and retrieval counts. No invented point-data URL.
                    url = BASE + f"/{COLLECTION}/ogc-api-coverages/1.0.0/collections/all/coverage/rangeset"
                    params = [("subset", f"lat({max(-90,latitude-.1)}:{min(90,latitude+.1)})"),
                        ("subset", f"lon({max(-180,longitude-.1)}:{min(180,longitude+.1)})"),
                        ("subset", f'time("{start}T00:00:00Z":"{end}T23:59:59Z")'),
                        ("format", "application/netcdf"), ("forceAsync", "true"), ("skipPreview", "true"), ("ignoreErrors", "false")]
                    job, response = get(url, params=params)
                    job_id = job.get("jobID")
                    if not job_id:
                        raise ValueError("Harmony did not return a job ID")
                    saved = {"job_id": job_id, "submitted_at": now(), "raw_objects": []}
                    cache.write(saved)
                    return missing("IMERG subset submitted; Final-run values remain unavailable while NASA processes the job.", "pending", job_id)
                job_id = saved["job_id"]
                job, _ = get(BASE + "/jobs/" + job_id)
                if job.get("status") != "successful":
                    state = "failed" if job.get("status") in ("failed", "canceled") else "pending"
                    if state == "pending" and job_timed_out(saved.get("submitted_at")):
                        state = "job_timeout"
                    return missing("IMERG extraction is " + state + "; no rainfall was assumed.", state, job_id)
                # Follow only NASA-provided output data links, including pagination.
                links = job.get("links", [])
                files = [link for link in links if link.get("rel") == "data"]
                next_links = [l for l in links if l.get("rel") == "next"]
                pages = 0
                while next_links:
                    pages += 1
                    if pages > 20:
                        raise ValueError("IMERG result pagination exceeds request bound")
                    page, _ = get(urljoin(BASE, next_links[0]["href"]))
                    files += [l for l in page.get("links", []) if l.get("rel") == "data"]
                    next_links = [l for l in page.get("links", []) if l.get("rel") == "next"]
                if not files or len(files) > 366:
                    raise ValueError("IMERG daily subset has an unexpected file count")
                if any(not public_url(link.get("href", "")).rsplit("/", 1)[-1].startswith(PRODUCT + "_") or
                       not public_url(link.get("href", "")).endswith(".nc4") for link in files):
                    raise ValueError("IMERG Harmony output filename does not identify Final V07")
                objects, points = [], []
                # Resume bounded downloads across calls; no long synchronous collection loop.
                completed = saved.get("collected", {})
                for link in files:
                    source = public_url(link["href"])
                    if source in completed:
                        continue
                    body, _ = fetch(self.session, "GET", link["href"], token=self.token, download=True)
                    if not (body.startswith(b"\x89HDF") or body.startswith(b"CDF")):
                        raise ValueError("IMERG Harmony output is not NetCDF")
                    raw = cache.raw(body, link["href"])
                    completed[source] = {"raw": raw, "points": [{**p,"raw_sha256":raw["sha256"],"source_file":raw["source"]} for p in parse_netcdf(body, query)]}
                    if len(completed) % 2 == 0:
                        cache.write({**saved, "collected": completed, "raw_objects": [v["raw"] for v in completed.values()]})
                        if len(completed) < len(files):
                            return missing("IMERG files are being validated and cached; repeat the same request to continue collection.", "collecting", job_id)
                for item in completed.values():
                    objects.append(item["raw"]); points += item["points"]
                rain = summarize(points, start, end)
                observed=sorted(p["date"] for p in rain["daily"] if p["value"] is not None)
                result = {"status": "available" if rain["coverage"]["valid_days"] else "unavailable", "provider": "GPM IMERG", "product": PRODUCT,
                    "access_status":"ready" if observed else "no_valid_observations", "reason":None if observed else "No daily IMERG precipitation passed the required coverage checks.",
                    "location": {"latitude": latitude, "longitude": longitude}, "period": {"start": start, "end": end}, "spatial_resolution": "0.1° latitude × 0.1° longitude",
                    "observation_period":{"start":observed[0],"end":observed[-1]} if observed else None,
                    "temporal_resolution": "daily (UTC); derived from half-hourly retrievals", "cache_status": "live_retrieved", "series": {"precipitation": rain},
                    "provenance": {"product": PRODUCT, "collection_id": COLLECTION, "access_method": "Harmony geographic subset; nearest native grid cell",
                        "query": query, "job_id": job_id, "submitted_at": saved.get("submitted_at"), "completed_at": job.get("updatedAt"),
                        "input_granules": job.get("numInputGranules"),
                        "subset_parameters": {"latitude": [max(-90, latitude-.1), min(90, latitude+.1)],
                                              "longitude": [max(-180, longitude-.1), min(180, longitude+.1)],
                                              "time": [start + "T00:00:00Z", end + "T23:59:59Z"], "format": "application/netcdf"},
                        "retrieved_at": now(), "raw_objects": objects, "source": "https://doi.org/10.5067/GPM/IMERGDF/DAY/07"},
                    "limitations": ["Final Run is delayed post-real-time research data; no near-real-time value or latency guarantee is fabricated.",
                        "Daily precipitation is mean rate in mm/day in V07, not the half-hourly mm/hour variable; counts must be 48 before accumulating a complete UTC day.",
                        "Satellite/gauge-combined regional estimates; coastal, terrain and snowfall errors remain. Not field irrigation demand or a forecast."]}
                cache.write({**saved, "profile": result, "raw_objects": objects})
                return result
            except (requests.RequestException, ValueError, KeyError, TypeError, OSError, ImportError, RuntimeError):
                return missing("IMERG access, NetCDF decoding or quality validation failed. Check authorized access and the saved Harmony job; rainfall remains unknown.", "access_or_data_error", (saved or {}).get("job_id"))
