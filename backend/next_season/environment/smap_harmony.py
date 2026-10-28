"""SMAP SPL4SMGP.008 extraction from observed Harmony NetCDF output."""

from datetime import date, datetime, timedelta, timezone
import json
import math
import os
from pathlib import Path
import re
import threading

import requests

from .cache import Cache, fetch, job_timed_out, now, public_url, unavailable
from .power import query_for

PRODUCT = "SPL4SMGP.008"
COLLECTION = "C3480440870-NSIDC_CPRD"
BASE = "https://harmony.earthdata.nasa.gov"
VARIABLES = {
    "surface_soil_moisture": ("sm_surface", "m3 m-3", 0.9),
    "root_zone_soil_moisture": ("sm_rootzone", "m3 m-3", 0.9),
    "root_zone_percentile": ("sm_rootzone_pctl", "percent", 100.0),
}
GRANULE = re.compile(r"SMAP_L4_SM_gph_(\d{8})T(\d{6})_(Vv8\d+)_\d+_subsetted\.nc4$")
_LOCK = threading.Lock()


def parse_harmony_netcdf(content, filename, query):
    import netCDF4
    import numpy as np

    match = GRANULE.fullmatch(filename)
    if not match:
        raise ValueError("Unexpected SMAP Harmony source granule")
    stamp = datetime.strptime(match.group(1) + match.group(2), "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    if not query["start"] <= stamp.date().isoformat() <= query["end"]:
        raise ValueError("SMAP granule outside requested dates")
    with netCDF4.Dataset("smap-harmony", memory=content) as ds:
        if "SMAP L4_SM Geophysical" not in getattr(ds, "Title", ""):
            raise ValueError("SMAP source title mismatch")
        if Path(getattr(ds, "Filename", "")).name != filename.replace("_subsetted.nc4", ".h5"):
            raise ValueError("SMAP native granule identity mismatch")
        lat, lon, t = (ds.variables[name] for name in ("cell_lat", "cell_lon", "time"))
        if lat.ndim != 2 or lon.shape != lat.shape or t.ndim != 1 or len(t) != 1:
            raise ValueError("Unsupported SMAP Harmony coordinate schema")
        lat_grid, lon_grid = np.asarray(lat[:]), np.asarray(lon[:])
        if not np.isfinite(lat_grid).all() or not np.isfinite(lon_grid).all():
            raise ValueError("SMAP grid coordinates are not finite")
        distance = (lat_grid - query["latitude"]) ** 2 + ((lon_grid - query["longitude"]) * math.cos(math.radians(query["latitude"]))) ** 2
        row, column = np.unravel_index(int(np.argmin(distance)), distance.shape)
        cell = {"latitude": float(lat_grid[row, column]), "longitude": float(lon_grid[row, column])}
        if abs(cell["latitude"] - query["latitude"]) > .1 or abs(cell["longitude"] - query["longitude"]) > .1:
            raise ValueError("SMAP grid cell is not near requested point")
        native = netCDF4.num2date(t[:], t.units, calendar=getattr(t, "calendar", "standard"))[0]
        native_time = datetime(native.year, native.month, native.day, native.hour, native.minute, native.second, native.microsecond, tzinfo=timezone.utc)
        if abs((native_time - stamp).total_seconds()) > 180:
            raise ValueError("SMAP native and granule times disagree")
        group = ds.groups["Geophysical_Data"]
        values = {}
        for name, (field, unit, maximum) in VARIABLES.items():
            var = group.variables[field]
            if var.dimensions != lat.dimensions or var.units != unit:
                raise ValueError("SMAP variable schema or units changed")
            scalar = var[row, column]
            value = None if np.ma.is_masked(scalar) else float(scalar)
            if value is not None and (not math.isfinite(value) or value < 0 or value > maximum):
                raise ValueError("SMAP source variable outside published range")
            values[name] = value
        return {"time": stamp.isoformat(), "native_time": native_time.isoformat(),
                "sampled_grid": cell, "native_granule_version": match.group(3), "values": values}


class SmapHarmonyProvider:
    def __init__(self, cache_dir, token=None, session=None):
        self.root = Path(cache_dir) / "smap"
        self.token = token if token is not None else (os.environ.get("EARTHDATA_TOKEN") or os.environ.get("NASA_EARTHDATA_TOKEN"))
        self.session = session or requests.Session()

    def profile(self, latitude, longitude, start, end):
        query_for(latitude, longitude, start, end)
        query = {"latitude": latitude, "longitude": longitude, "start": start, "end": end,
                 "product": PRODUCT, "collection_id": COLLECTION, "variables": list(VARIABLES),
                 "access_method": "Harmony geographic subset", "adapter_version": 2}
        cache = Cache(self.root, query)

        def missing(reason, state="unavailable", job=None):
            return unavailable("SMAP", PRODUCT, query, reason, access="Harmony geographic subset / NetCDF",
                               resolution="9 km EASE-Grid 2.0", temporal="3-hourly", state=state, job_id=job)

        with _LOCK:
            saved = cache.read()
            if saved and saved.get("profile"):
                result = saved["profile"]
                result["cache_status"] = "cached"
                return result
            if not self.token:
                return missing("SMAP Harmony extraction requires an Earthdata bearer token in the backend environment.", "authentication_required")
            try:
                def get(url, **kwargs):
                    body, _ = fetch(self.session, "GET", url, token=self.token, **kwargs)
                    return json.loads(body)

                if not saved:
                    url = BASE + f"/{COLLECTION}/ogc-api-coverages/1.0.0/collections/all/coverage/rangeset"
                    params = [("subset", f"lat({max(-90, latitude-.1)}:{min(90, latitude+.1)})"),
                              ("subset", f"lon({max(-180, longitude-.1)}:{min(180, longitude+.1)})"),
                              ("subset", f'time("{start}T00:00:00Z":"{end}T23:59:59Z")'),
                              ("format", "application/netcdf"), ("forceAsync", "true"),
                              ("skipPreview", "true"), ("ignoreErrors", "false")]
                    job = get(url, params=params)
                    job_id = job.get("jobID")
                    if not job_id:
                        raise ValueError("Harmony did not return a SMAP job ID")
                    saved = {"job_id": job_id, "submitted_at": now(), "raw_objects": []}
                    cache.write(saved)
                    return missing("SMAP subset submitted; values are unavailable while NASA processes the job.", "pending", job_id)

                job_id = saved["job_id"]
                job = get(BASE + "/jobs/" + job_id)
                if job.get("status") != "successful":
                    state = "failed" if job.get("status") in ("failed", "canceled") else "pending"
                    if state == "pending" and job_timed_out(saved.get("submitted_at")):
                        state = "job_timeout"
                    return missing("SMAP extraction is " + state + "; no moisture was assumed.", state, job_id)
                links = [link for link in job.get("links", []) if link.get("rel") == "data" and public_url(link.get("href", "")).endswith(".nc4")]
                if not links or len(links) > 3000:
                    raise ValueError("Unexpected SMAP Harmony output count")
                completed = saved.get("collected", {})
                new_count = 0
                for link in links:
                    source = public_url(link["href"])
                    filename = source.rsplit("/", 1)[-1]
                    match = GRANULE.fullmatch(filename)
                    if not match:
                        raise ValueError("Unexpected SMAP Harmony output filename")
                    day = date(int(match.group(1)[:4]), int(match.group(1)[4:6]), int(match.group(1)[6:8])).isoformat()
                    if not start <= day <= end or source in completed:
                        continue
                    body, response = fetch(self.session, "GET", link["href"], token=self.token, download=True)
                    if not (body.startswith(b"\x89HDF") or body.startswith(b"CDF")):
                        raise ValueError("SMAP Harmony output is not NetCDF")
                    point = parse_harmony_netcdf(body, filename, query)
                    raw = cache.raw(body, link["href"])
                    completed[source] = {"point": {**point, "raw_sha256": raw["sha256"], "source_file": source}, "raw": raw,
                                         "content_type": response.headers.get("Content-Type")}
                    new_count += 1
                    if new_count >= 2:
                        cache.write({**saved, "collected": completed, "raw_objects": [v["raw"] for v in completed.values()]})
                        return missing("SMAP source files are being verified and cached; repeat the same request.", "collecting", job_id)
                points = sorted((v["point"] for v in completed.values()), key=lambda p: p["time"])
                expected = (date.fromisoformat(end) - date.fromisoformat(start)).days * 8 + 8
                if len(points) != expected or any(datetime.fromisoformat(b["time"]) - datetime.fromisoformat(a["time"]) != timedelta(hours=3) for a, b in zip(points, points[1:])):
                    raise ValueError("SMAP Harmony extraction lacks the expected three-hour coverage")
                series = {}
                for name, (_, unit, _) in VARIABLES.items():
                    samples = [{"time": p["time"], "value": p["values"][name], "native_time": p["native_time"],
                                "sampled_grid": p["sampled_grid"], "raw_sha256": p["raw_sha256"]} for p in points]
                    valid = [p["value"] for p in samples if p["value"] is not None]
                    series[name] = {"unit": "percentile" if name == "root_zone_percentile" else "m3/m3", "points": samples,
                                    "mean": sum(valid) / len(valid) if valid else None,
                                    "coverage": {"valid_samples": len(valid), "expected_samples": expected, "complete": len(valid) == expected}}
                observed = [p["time"] for p in points if any(v is not None for v in p["values"].values())]
                raw_objects = [v["raw"] for v in completed.values()]
                result = {"status": "available" if observed else "unavailable", "provider": "SMAP", "product": PRODUCT,
                          "access_status": "ready" if observed else "no_valid_observations", "reason": None if observed else "No SMAP values passed source quality checks.",
                          "location": {"latitude": latitude, "longitude": longitude}, "period": {"start": start, "end": end},
                          "observation_period": {"start": observed[0], "end": observed[-1]} if observed else None,
                          "spatial_resolution": "9 km EASE-Grid 2.0", "temporal_resolution": "3-hourly", "cache_status": "live_retrieved",
                          "series": series, "depths": {"surface_soil_moisture": "0–5 cm", "root_zone_soil_moisture": "0–100 cm"},
                          "provenance": {"product": PRODUCT, "collection_id": COLLECTION, "access_method": "Harmony geographic subset; nearest native grid cell",
                                         "query": query, "job_id": job_id, "submitted_at": saved.get("submitted_at"),
                                         "completed_at": job.get("updatedAt"), "input_granules": job.get("numInputGranules"),
                                         "subset_parameters": {"latitude": [max(-90, latitude-.1), min(90, latitude+.1)],
                                                               "longitude": [max(-180, longitude-.1), min(180, longitude+.1)],
                                                               "time": [start + "T00:00:00Z", end + "T23:59:59Z"],
                                                               "format": "application/netcdf"},
                                         "retrieved_at": now(), "raw_objects": raw_objects,
                                         "native_granule_versions": sorted({p["native_granule_version"] for p in points}),
                                         "source": "https://nsidc.org/data/spl4smgp/versions/8"},
                          "limitations": ["Assimilated 9 km land-model estimates, not field measurements.",
                                          "The granule filename timestamp is retained alongside the NetCDF native time, which differs by about one minute in the validated output.",
                                          "Masked percentile samples remain unknown; percentile 50 is a product seasonal median, not a crop-damage threshold."]}
                cache.write({**saved, "profile": result, "raw_objects": raw_objects})
                return result
            except (requests.RequestException, ValueError, KeyError, TypeError, OSError, RuntimeError, ImportError):
                return missing("SMAP Harmony access, NetCDF decoding or quality validation failed; moisture remains unknown.",
                               "access_or_data_error", (saved or {}).get("job_id"))
