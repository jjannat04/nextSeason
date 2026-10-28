"""Independent NASA adapters combined without cross-source substitution."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from .power import PowerProvider, query_for
from .smap import SmapProvider
from .gpm import GpmProvider
from .cache import now, unavailable
from .indicators import interpret


class EnvironmentalProfile:
    def __init__(self, cache_dir, *, power=None, smap=None, gpm=None, satellite_cache_dir=None):
        cache_dir=Path(cache_dir)
        satellite_cache_dir=Path(satellite_cache_dir) if satellite_cache_dir is not None else cache_dir/"environment"
        self.providers = {"power": power or PowerProvider(cache_dir / "power"),
            "smap": smap or SmapProvider(satellite_cache_dir), "gpm": gpm or GpmProvider(satellite_cache_dir)}

    def profile(self, latitude, longitude, start, end, comparison_period=None):
        query_for(latitude, longitude, start, end)
        query = {"latitude": latitude, "longitude": longitude, "start": start, "end": end}
        def attempt(name, first=start, last=end):
            try:
                return self.providers[name].profile(latitude, longitude, first, last)
            except Exception:
                # Operational failure is isolated; do not expose requests/credentials.
                products = {"power": "NASA POWER daily AG", "smap": "SPL4SMGP.008", "gpm": "GPM_3IMERGDF.07"}
                return unavailable(name.upper(), products[name], {**query, "start": first, "end": last}, "Provider request failed; values remain unavailable.",
                    access="Independent provider adapter", resolution="See product metadata", temporal="See product metadata", state="provider_error")
        with ThreadPoolExecutor(max_workers=3) as executor:
            pending = {name: executor.submit(attempt, name) for name in self.providers}
            values = {name: job.result() for name, job in pending.items()}
        baseline = attempt("gpm", comparison_period["start"], comparison_period["end"]) if comparison_period else None
        provenance = {name: value.get("provenance", {"provider": value.get("provider"), "query": value.get("query"), "source": value.get("request_url"),
            "retrieved_at": value.get("retrieved_at"), "response_sha256": value.get("response_sha256"), "source_metadata": value.get("source_metadata")}) for name, value in values.items()}
        if baseline:
            provenance["gpm_comparison"] = baseline.get("provenance")
        return {"location": {"latitude": latitude, "longitude": longitude}, **values,
            "interpreted_indicators": interpret(values["smap"], values["gpm"], baseline),
            "provenance": {"assembled_at": now(), "providers": provenance},
            "provider_status": {name: {"status": value["status"], "access_status": value.get("access_status", "ready"), "cache_status": value.get("cache_status"), "reason": value.get("reason")} for name, value in values.items()},
            "comparison_period": comparison_period,
            "limitations": ["Independent products have different spatial grids, temporal sampling, processing methods and latency; they are not interchangeable field measurements.",
                "Historical selected-period context is not current weather or a forecast. Missing providers are not replaced by POWER precipitation or synthetic values.",
                "No irrigation amount, crop-stage damage or flood probability is calculated from these indicators."]}
