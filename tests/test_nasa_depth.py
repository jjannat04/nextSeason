"""Synthetic source-shaped data only in tests; real adapters/provenance contracts."""
import csv
from datetime import date, timedelta
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import netCDF4
import numpy as np
import requests
from django.test import Client
from test_milestone1 import TestProvider
from test_prototype import request_data
from next_season.environment.cache import Cache, fetch, number
from next_season.environment.smap import SmapProvider, parse_csv, LAYERS
from next_season.environment.smap_harmony import SmapHarmonyProvider, parse_harmony_netcdf
from next_season.environment.gpm import GpmProvider, parse_netcdf, summarize
from next_season.environment.profile import EnvironmentalProfile
from next_season.environment.indicators import moisture, rainfall, rainfall_comparison
from next_season.engine.service import plan
from next_season.knowledge.repository import load_dataset
from next_season.engine.environmental_evaluation import annual_rainfall
from next_season.environment.power import normalize,query_for,PARAMETERS


class Response:
    def __init__(self, value, headers=None, status_code=200):
        self.body = value if isinstance(value, bytes) else json.dumps(value).encode()
        self.status_code = status_code
        self.headers = headers or {}
    def iter_content(self, size):
        yield self.body
    def raise_for_status(self):
        pass


class Session:
    def __init__(self, responses): self.responses, self.calls = list(responses), []
    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        if not self.responses: raise AssertionError("Unexpected network request")
        return self.responses.pop(0)


class Failure:
    def profile(self, *args): raise RuntimeError("Provider operational failure")


class RequestFailureSession:
    def __init__(self, exception): self.exception = exception
    def request(self, *args, **kwargs): raise self.exception


def smap_csv(percentile=20, surface=.2):
    stream = io.StringIO()
    columns = ["Latitude", "Longitude", "Date", "Time"] + [f"SPL4SMGP_008_{v}" for v in LAYERS.values()]
    writer = csv.DictWriter(stream, fieldnames=columns); writer.writeheader()
    for hour in range(0, 24, 3):
        writer.writerow(dict(zip(columns, [22.8, 89.55, "2024-01-01", f"{hour:02}:00:00", surface, .3, percentile])))
    return stream.getvalue().encode()


def nc_bytes(values=(2,), counts=(48,), unit="mm/day", lon=89.55, doi="10.5067/GPM/IMERGDF/DAY/07"):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "synthetic-test-only.nc4"
        with netCDF4.Dataset(path, "w") as data:
            data.title = "GPM IMERG Final Precipitation L3 1 day 0.1 degree x 0.1 degree (GPM_3IMERGDF)"
            data.DOI = doi
            data.BeginDate = "2024-01-01"
            data.EndDate = (date(2024,1,1) + timedelta(days=len(values)-1)).isoformat()
            data.ProductionTime = "2024-06-12T14:19:57.862Z"
            for dim, size in (("time", len(values)), ("lat", 1), ("lon", 1)): data.createDimension(dim, size)
            lat = data.createVariable("lat", "f8", ("lat",)); lat.units = "degrees_north"; lat[:] = [22.8]
            lng = data.createVariable("lon", "f8", ("lon",)); lng.units = "degrees_east"; lng[:] = [lon]
            time = data.createVariable("time", "f8", ("time",)); time.units = "days since 2024-01-01 00:00:00"; time[:] = np.arange(len(values))
            rain = data.createVariable("precipitation", "f4", ("time", "lon", "lat"), fill_value=-9999.9); rain.units = unit
            count = data.createVariable("precipitation_cnt", "i4", ("time", "lon", "lat")); count.units = "count"
            rain[:, 0, 0] = values; count[:, 0, 0] = counts
        return path.read_bytes()


def smap_harmony_bytes():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "synthetic-smap.nc4"
        with netCDF4.Dataset(path, "w") as data:
            data.createDimension("y", 1); data.createDimension("x", 1); data.createDimension("dim1", 1)
            data.Title = "SMAP L4_SM Geophysical (GPH) Data Granule"
            data.Filename = "/native/SMAP_L4_SM_gph_20240101T013000_Vv8012_001.h5"
            lat = data.createVariable("cell_lat", "f4", ("y", "x")); lat[:] = [[22.7883]]
            lon = data.createVariable("cell_lon", "f4", ("y", "x")); lon[:] = [[89.5799]]
            time = data.createVariable("time", "f8", ("dim1",))
            time.units = "seconds since 2024-01-01 01:28:55.816"
            time[:] = [0]
            group = data.createGroup("Geophysical_Data")
            for name, value, unit in (("sm_surface", .31, "m3 m-3"), ("sm_rootzone", .37, "m3 m-3"), ("sm_rootzone_pctl", 65, "percent")):
                v = group.createVariable(name, "f4", ("y", "x"), fill_value=-9999)
                v.units = unit; v[:] = [[value]]
        return path.read_bytes()


def gpm_year(total):
    points = [{"date": (date(2024,1,1)+timedelta(days=i)).isoformat(), "value": total/366, "valid_half_hour_samples": 48} for i in range(366)]
    return {"status":"available", "provider":"GPM IMERG", "product":"GPM_3IMERGDF.07", "location":{"latitude":22.8,"longitude":89.55},
        "period":{"start":"2024-01-01","end":"2024-12-31"}, "series":{"precipitation":summarize(points,"2024-01-01","2024-12-31")},
        "provenance":{"product":"GPM_3IMERGDF.07","raw_objects":[{"sha256":"test-source-checksum"}]}}


def smap_year(percentile):
    points = [{"time": (date(2024,1,1)+timedelta(days=i)).isoformat()+"T01:30:00+00:00", "value":percentile} for i in range(366)]
    return {"status":"available", "provider":"SMAP", "product":"SPL4SMGP.008", "series":{"root_zone_percentile":{"points":points,"mean":percentile,"coverage":{"complete":True}}},
        "provenance":{"product":"SPL4SMGP.008","raw_objects":[{"sha256":"test-smap-source-checksum"}]}}


class Fixed:
    def __init__(self, result): self.result=result
    def profile(self, *args): return self.result


class AnnualPower:
    def profile(self, latitude, longitude, start, end):
        days=[(date(2024,1,1)+timedelta(days=i)).strftime("%Y%m%d") for i in range(366)]
        raw={"header":{"fill_value":-999,"title":"Synthetic test-only full-year source"},"parameters":{p:{"units":"mm/day" if p=="PRECTOTCORR" else "C"} for p in PARAMETERS},
            "properties":{"parameter":{p:{d:2 if p=="PRECTOTCORR" else 22 for d in days} for p in PARAMETERS}}}
        return normalize(raw,query_for(latitude,longitude,start,end),retrieved_at="2026-10-28T00:00:00+00:00",cache_status="synthetic_test_only")


class NasaDepthTests(unittest.TestCase):
    def test_power_independent_of_both_optional_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = EnvironmentalProfile(Path(tmp), power=TestProvider(), smap=Failure(), gpm=Failure())
            result = service.profile(22.8,89.55,"2024-01-01","2024-01-03")
        self.assertEqual(result["power"]["status"],"available")
        self.assertEqual(result["power"]["series"]["T2M"]["mean"],22)
        for name in ("smap","gpm"):
            self.assertEqual(result[name]["status"],"unavailable")
            self.assertEqual(result[name]["series"],{})
            self.assertIsNone(result[name]["summary"])

    def test_one_optional_failure_does_not_hide_other_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            for smap, gpm, expected in ((Failure(),Fixed(gpm_year(1200)),"gpm"),(Fixed(smap_year(20)),Failure(),"smap")):
                result=EnvironmentalProfile(Path(tmp),power=TestProvider(),smap=smap,gpm=gpm).profile(22.8,89.55,"2024-01-01","2024-01-03")
                self.assertEqual(result[expected]["status"],"available")
                self.assertEqual(result["provenance"]["providers"][expected]["product"],result[expected]["product"])

    def test_no_credentials_returns_unavailable_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            for provider in (SmapProvider(tmp,token="",session=Session([])),GpmProvider(tmp,token="",session=Session([]))):
                result=provider.profile(22.8,89.55,"2024-01-01","2024-01-01")
                self.assertEqual(result["status"],"unavailable")
                self.assertEqual(result["access_status"],"authentication_required")
                self.assertEqual(result["series"],{})

    def test_earthdata_token_environment_alias_is_private(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict("os.environ", {"EARTHDATA_TOKEN": "synthetic-test-token", "NASA_EARTHDATA_TOKEN": ""}):
            provider = GpmProvider(tmp, session=RequestFailureSession(requests.Timeout()))
            self.assertEqual(provider.token, "synthetic-test-token")
            result = provider.profile(22.8,89.55,"2024-01-01","2024-01-01")
            self.assertEqual(result["status"], "unavailable")
            self.assertEqual(result["access_status"], "access_or_data_error")
            self.assertEqual(result["series"], {})
            self.assertNotIn("synthetic-test-token", json.dumps(result))
            self.assertEqual(list(Path(tmp).rglob("*")), [])

    def test_invalid_token_and_request_timeout_do_not_become_zero(self):
        for exception in (requests.HTTPError("401 Unauthorized"), requests.Timeout()):
            with tempfile.TemporaryDirectory() as tmp:
                for provider in (SmapProvider(tmp, token="synthetic-test-token", session=RequestFailureSession(exception)),
                                 GpmProvider(tmp, token="synthetic-test-token", session=RequestFailureSession(exception))):
                    result = provider.profile(22.8,89.55,"2024-01-01","2024-01-01")
                    self.assertEqual(result["status"], "unavailable")
                    self.assertEqual(result["access_status"], "access_or_data_error")
                    self.assertEqual(result["series"], {})
                    self.assertIsNone(result["summary"])

    def test_empty_or_corrupt_downloaded_source_is_rejected(self):
        query = {"latitude":22.8,"longitude":89.55,"start":"2024-01-01","end":"2024-01-01"}
        with self.assertRaises(ValueError): parse_csv(b"", query)
        with self.assertRaises((OSError, RuntimeError, ValueError)): parse_netcdf(b"corrupt", query)

    def test_live_observed_smap_harmony_schema_parser(self):
        query = {"latitude":22.8,"longitude":89.55,"start":"2024-01-01","end":"2024-01-01"}
        name = "SMAP_L4_SM_gph_20240101T013000_Vv8012_001_subsetted.nc4"
        result = parse_harmony_netcdf(smap_harmony_bytes(), name, query)
        self.assertEqual(result["time"], "2024-01-01T01:30:00+00:00")
        self.assertEqual(result["native_granule_version"], "Vv8012")
        self.assertAlmostEqual(result["values"]["surface_soil_moisture"], .31, places=5)
        self.assertAlmostEqual(result["sampled_grid"]["latitude"], 22.7883, places=3)
        with self.assertRaises(ValueError): parse_harmony_netcdf(smap_harmony_bytes(), name.replace("Vv8012", "Vv7021"), query)
        with self.assertRaises((OSError, RuntimeError, ValueError)): parse_harmony_netcdf(b"corrupt", name, query)

    def test_harmony_cloudfront_redirect_never_receives_bearer_token(self):
        target = "https://dqzb5lcolc8fj.cloudfront.net/verified-output.nc4?signature=test-only"
        session = Session([Response(b"", {"Location":target}, 307), Response(b"\x89HDFsynthetic")])
        body, _ = fetch(session, "GET", "https://harmony.earthdata.nasa.gov/jobs/test-only/data", token="synthetic-test-token", download=True)
        self.assertTrue(body.startswith(b"\x89HDF"))
        self.assertIn("Authorization", session.calls[0][2]["headers"])
        self.assertNotIn("Authorization", session.calls[1][2]["headers"])

    def test_pending_nasa_job_over_24_hours_is_explicit_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            gpm_query={"latitude":22.8,"longitude":89.55,"start":"2024-01-01","end":"2024-01-01",
                       "product":"GPM_3IMERGDF.07","collection_id":"C2723754864-GES_DISC",
                       "variables":["precipitation","precipitation_cnt","lat","lon","time"],"adapter_version":1}
            smap_query={"latitude":22.8,"longitude":89.55,"start":"2024-01-01","end":"2024-01-01",
                        "product":"SPL4SMGP.008","collection_id":"C3480440870-NSIDC_CPRD",
                        "variables":["surface_soil_moisture","root_zone_soil_moisture","root_zone_percentile"],
                        "access_method":"Harmony geographic subset","adapter_version":2}
            for provider, path, query in ((GpmProvider(tmp,token="synthetic-test-token",session=Session([Response({"status":"running"})])),
                                          Path(tmp)/"gpm",gpm_query),
                                         (SmapHarmonyProvider(tmp,token="synthetic-test-token",session=Session([Response({"status":"running"})])),
                                          Path(tmp)/"smap",smap_query)):
                Cache(path,query).write({"job_id":"old-job","submitted_at":"2020-01-01T00:00:00+00:00","raw_objects":[]})
                result=provider.profile(22.8,89.55,"2024-01-01","2024-01-01")
                self.assertEqual(result["access_status"],"job_timeout")
                self.assertEqual(result["series"],{})

    def test_smap_point_csv_units_fills_and_real_zero(self):
        q={"latitude":22.8,"longitude":89.55,"start":"2024-01-01","end":"2024-01-01"}
        parsed=parse_csv(smap_csv(0,0),q)
        self.assertEqual(parsed["surface_soil_moisture"]["mean"],0)
        self.assertEqual(parsed["root_zone_percentile"]["mean"],0)
        self.assertEqual(parsed["root_zone_soil_moisture"]["unit"],"m3/m3")
        self.assertTrue(parsed["surface_soil_moisture"]["coverage"]["complete"])
        parsed=parse_csv(smap_csv(-9999,-9999),q)
        self.assertIsNone(parsed["surface_soil_moisture"]["mean"])
        self.assertFalse(parsed["root_zone_percentile"]["coverage"]["complete"])

    def test_smap_missing_time_point_mismatch_or_duplicate_rejected(self):
        q={"latitude":22.8,"longitude":89.55,"start":"2024-01-01","end":"2024-01-01"}
        with self.assertRaises(ValueError):parse_csv(smap_csv().replace(b"00:00:00",b""),q)
        with self.assertRaises(ValueError):parse_csv(smap_csv().replace(b"22.8",b"25.8"),q)
        with self.assertRaises(ValueError):parse_csv(smap_csv().replace(b"22.8",b"nan"),q)
        content=smap_csv(); content+=content.splitlines(keepends=True)[1]
        with self.assertRaises(ValueError):parse_csv(content,q)

    def test_smap_async_submit_collect_cache_and_provenance(self):
        content=smap_csv()
        session=Session([Response({"task_id":"task-one","status":"pending"}),Response({"status":"done"}),
            Response({"files":[{"file_name":"next-season-SPL4SMGP-008-results.csv","file_id":"f-one","sha256":hashlib.sha256(content).hexdigest()}]}),Response(content)])
        with tempfile.TemporaryDirectory() as tmp:
            provider=SmapProvider(tmp,token="secret-token-test",session=session)
            args=(22.8,89.55,"2024-01-01","2024-01-01")
            self.assertEqual(provider.profile(*args)["access_status"],"pending")
            result=provider.profile(*args)
            self.assertEqual(result["status"],"available")
            self.assertEqual(result["provenance"]["job_id"],"task-one")
            self.assertEqual(result["provenance"]["raw_objects"][0]["sha256"],hashlib.sha256(content).hexdigest())
            self.assertEqual(provider.profile(*args)["cache_status"],"cached")
            self.assertEqual(len(session.calls),4)
            for path in Path(tmp).rglob("*.json"):self.assertNotIn("secret-token-test",path.read_text())
            self.assertNotIn("secret-token-test",json.dumps(result))

    def test_imerg_native_netcdf_units_mask_counts_and_grid(self):
        q={"latitude":22.8,"longitude":89.55,"start":"2024-01-01","end":"2024-01-03"}
        points=parse_netcdf(nc_bytes((0,-9999.9,4),(48,48,47)),q)
        self.assertEqual(points[0]["value"],0)
        self.assertIsNone(points[1]["value"])
        self.assertIsNone(points[2]["value"])
        result=summarize(points,q["start"],q["end"])
        self.assertIsNone(result["total_mm"])
        self.assertFalse(result["coverage"]["complete"])
        with self.assertRaises(ValueError):parse_netcdf(nc_bytes(unit="mm/hr"),q)
        with self.assertRaises(ValueError):parse_netcdf(nc_bytes(doi="different-product"),q)
        with self.assertRaises(ValueError):parse_netcdf(nc_bytes(lon=60),q)
        with self.assertRaises(ValueError):parse_netcdf(nc_bytes(lon=float('nan')),q)
        self.assertEqual(gpm_year(0)["series"]["precipitation"]["total_mm"],0)

    def test_imerg_missing_dates_not_zero_and_no_duplicate_accumulation(self):
        point={"date":"2024-01-01","value":2}
        result=summarize([point],"2024-01-01","2024-01-02")
        self.assertIsNone(result["daily"][1]["value"])
        self.assertIsNone(result["total_mm"])
        with self.assertRaises(ValueError):summarize([point,point],"2024-01-01","2024-01-01")

    def test_imerg_async_native_collection_and_cache(self):
        content=nc_bytes()
        session=Session([Response({"jobID":"gpm-job","status":"running"}),Response({"jobID":"gpm-job","status":"successful","links":[{"rel":"data","href":"https://example.s3.amazonaws.com/GPM_3IMERGDF.07_test_subsetted.nc4?signature=private"}]}),Response(content)])
        with tempfile.TemporaryDirectory() as tmp:
            provider=GpmProvider(tmp,token="secret-edl",session=session)
            args=(22.8,89.55,"2024-01-01","2024-01-01")
            self.assertEqual(provider.profile(*args)["access_status"],"pending")
            result=provider.profile(*args)
            self.assertEqual(result["series"]["precipitation"]["total_mm"],2)
            self.assertNotIn("signature=",json.dumps(result))
            self.assertNotIn("Authorization",session.calls[-1][2]["headers"])
            self.assertEqual(provider.profile(*args)["cache_status"],"cached")
            self.assertEqual(len(session.calls),3)

    def test_cache_query_and_raw_checksums_are_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache=Cache(tmp,{"latitude":22.8}); raw=cache.raw(b"original","https://nasa.gov/source?secret=one")
            cache.write({"raw_objects":[raw],"number":1})
            self.assertIsNotNone(cache.read())
            self.assertIsNone(Cache(tmp,{"latitude":25}).read())
            (Path(tmp)/"raw"/raw["sha256"]).write_bytes(b"corrupt")
            self.assertIsNone(cache.read())
            cache.raw(b"original","https://nasa.gov/source")
            self.assertIsNotNone(cache.read())

    def test_unsafe_hosts_and_nonfinite_values_never_enter_data(self):
        with self.assertRaises(ValueError):fetch(Session([]),"GET","http://example.org",token="secret")
        with self.assertRaises(ValueError):fetch(Session([]),"GET","https://example.org",token="secret")
        for value in (None,"",-9999,float('nan')):self.assertIsNone(number(value))
        self.assertEqual(number(0),0)

    def test_percentile_indicator_changes_without_invented_water_threshold(self):
        low=moisture(smap_year(20)); high=moisture(smap_year(80))
        self.assertNotEqual(low["value"],high["value"])
        self.assertEqual(low["exact_values"]["below_median_fraction"],1)
        self.assertEqual(high["exact_values"]["below_median_fraction"],0)
        self.assertIn("not a crop drought threshold",low["method"])
        self.assertIsNone(moisture({"status":"unavailable"})["value"])

    def test_rainfall_anomaly_requires_comparable_source_windows(self):
        selected=gpm_year(800); other=gpm_year(1600)
        other["period"]={"start":"2023-01-01","end":"2023-12-31"}
        result=rainfall_comparison(selected,other)
        self.assertEqual(result["value"],"drier_than_selected_comparison")
        self.assertIsNone(rainfall_comparison(selected,None)["value"])
        other["location"]["longitude"]=80
        self.assertEqual(rainfall_comparison(selected,other)["status"],"insufficient_data")

    def test_only_complete_annual_rainfall_is_compared_with_annual_requirements(self):
        crop=next(c for c in load_dataset("prototype_recommendation")["crops"] if c["id"]=="maize")
        self.assertEqual(annual_rainfall(crop,gpm_year(800))["value"],"good_fit")
        self.assertEqual(annual_rainfall(crop,gpm_year(3000))["value"],"potential_concern")
        partial=gpm_year(800);partial["period"]["end"]="2024-03-31"
        self.assertEqual(annual_rainfall(crop,partial)["status"],"insufficient_data")

    def test_gpm_values_can_change_rotation_climate_and_rank(self):
        data=request_data(); data["historical_period"]={"start":"2024-01-01","end":"2024-12-31"}; data["priorities"]={"climate_suitability":1}
        with tempfile.TemporaryDirectory() as tmp:
            def run(total):
                provider=EnvironmentalProfile(Path(tmp),power=AnnualPower(),smap=Failure(),gpm=Fixed(gpm_year(total)))
                return plan(data,TestProvider(),environmental_provider=provider)
            first,second=run(800),run(1700)
        ranks=lambda r:{c["id"]:c["rank"] for c in r["candidate_rotations"]}
        self.assertNotEqual(ranks(first),ranks(second))
        for c in second["candidate_rotations"]:
            self.assertIn("GPM IMERG",c["dimension_results"]["climate_suitability"]["sources_used"])
            evidence=[e for e in c["explanations"] if e["dimension"]=="rainfall_suitability"][0]
            self.assertEqual(evidence["environment_source"][0]["product"],"GPM_3IMERGDF.07")

    def test_smap_changes_rotation_context_without_damage_claim(self):
        data=request_data(); data["priorities"]={"moisture_context":1}
        with tempfile.TemporaryDirectory() as tmp:
            def run(value):
                return plan(data,TestProvider(),environmental_provider=EnvironmentalProfile(Path(tmp),power=TestProvider(),smap=Fixed(smap_year(value)),gpm=Failure()))
            first,second=run(20),run(80)
        dimension=lambda result:result["candidate_rotations"][0]["dimension_results"]["historical_moisture_context"]
        self.assertNotEqual(dimension(first)["value"],dimension(second)["value"])
        self.assertEqual(first["ranking"]["priority_order"],["moisture_context"])
        self.assertEqual(dimension(first)["comparison_direction"],"lower_is_preferred")

    def test_both_failures_do_not_block_real_rotations_or_penalize_climate(self):
        data=request_data()
        with tempfile.TemporaryDirectory() as tmp:
            result=plan(data,TestProvider(),environmental_provider=EnvironmentalProfile(Path(tmp),power=TestProvider(),smap=Failure(),gpm=Failure()))
        self.assertTrue(result["candidate_rotations"])
        self.assertTrue(result["is_recommendation"])
        for c in result["candidate_rotations"]:
            self.assertEqual(c["dimension_results"]["climate_suitability"]["sources_used"],["NASA POWER"])
            self.assertIsNone(c["dimension_results"]["rainfall_suitability"]["value"])

    def test_unified_endpoint_contract_and_validation(self):
        data={"location":{"latitude":22.8,"longitude":89.55},"historical_period":{"start":"2024-01-01","end":"2024-01-03"}}
        with tempfile.TemporaryDirectory() as tmp:
            provider=EnvironmentalProfile(Path(tmp),power=TestProvider(),smap=Failure(),gpm=Failure())
            with patch("next_season.api.views.environmental_provider",return_value=provider):
                response=Client().post("/api/environment-profile",data=json.dumps(data),content_type="application/json")
        self.assertEqual(response.status_code,200)
        self.assertTrue({"location","power","smap","gpm","interpreted_indicators","provenance","provider_status","limitations"}<=set(response.json()))
        data["rainfall_comparison_period"]={"start":"2023-02-01","end":"2023-02-03"}
        response=Client().post("/api/environment-profile",data=json.dumps(data),content_type="application/json")
        self.assertEqual(response.status_code,400)
