"""Private exact-query caches and bounded, credential-safe NASA transport."""
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
from urllib.parse import urlsplit, urlunsplit
import requests


def now():
    return datetime.now(timezone.utc).isoformat()


def job_timed_out(submitted_at, hours=24):
    """Operational warning only; a later completed NASA job may still be accepted."""
    try:
        submitted = datetime.fromisoformat(submitted_at.replace("Z", "+00:00"))
        return submitted.tzinfo is not None and datetime.now(timezone.utc) - submitted > timedelta(hours=hours)
    except (AttributeError, TypeError, ValueError):
        return False


def digest(value):
    return hashlib.sha256(value).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, allow_nan=False).encode()


def public_url(url):
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def trusted(url, download=False):
    parts = urlsplit(url)
    host = parts.hostname or ""
    if parts.scheme != "https" or parts.username or parts.password:
        raise ValueError("Untrusted NASA resource URL")
    # Harmony's authenticated output link redirects to this NASA staging CDN.
    # Authorization is stripped on the cross-host redirect below.
    if not (host.endswith(".nasa.gov") or download and (host.endswith(".amazonaws.com") or host == "dqzb5lcolc8fj.cloudfront.net")):
        raise ValueError("Unexpected NASA resource host")
    return url


def fetch(session, method, url, *, token=None, download=False, limit=16_000_000, **kwargs):
    trusted(url, download)
    # NASA may provide an output URL already pointing at signed object storage.
    # Never send a bearer token to that host, even on the initial request.
    headers = {"Authorization": f"Bearer {token}"} if token and (urlsplit(url).hostname or "").endswith(".nasa.gov") else {}
    # Redirects are handled explicitly; never send credentials to a signed S3 URL.
    for _ in range(6):
        response = session.request(method, url, headers=headers, timeout=(4, 12), allow_redirects=False, stream=True, **kwargs)
        if response.status_code in (301, 302, 303, 307, 308):
            from urllib.parse import urljoin
            target = trusted(urljoin(url, response.headers["Location"]), download)
            if urlsplit(target).hostname != urlsplit(url).hostname:
                headers = {}
            url, method, kwargs = target, "GET", {}
            continue
        response.raise_for_status()
        chunks, size = [], 0
        for chunk in response.iter_content(65536):
            size += len(chunk)
            if size > limit:
                raise ValueError("NASA response exceeds the bounded subset size")
            chunks.append(chunk)
        return b"".join(chunks), response
    raise ValueError("Too many NASA redirects")


def number(value, minimum=0, maximum=None, fills=(-9999, -999, -9999.9)):
    if value is None or str(value).strip().lower() in ("", "nan", "null", "n/a"):
        return None
    value = float(value)
    if not math.isfinite(value) or value in fills or value < minimum or maximum is not None and value > maximum:
        return None
    return value


class Cache:
    def __init__(self, root, query):
        self.root = Path(root)
        self.query = query
        self.key = digest(encoded(query))
        self.path = self.root / (self.key + ".json")

    def write(self, value):
        self.root.mkdir(parents=True, exist_ok=True)
        payload = {"query": self.query, "value": value, "sha256": digest(encoded(value))}
        fd, temp = tempfile.mkstemp(dir=self.root, suffix=".tmp")
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(encoded(payload))
            os.replace(temp, self.path)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)

    def read(self):
        try:
            record = json.loads(self.path.read_text(encoding="utf-8"))
            if record["query"] != self.query or record["sha256"] != digest(encoded(record["value"])):
                return None
            for raw in record["value"].get("raw_objects", []):
                path = self.root / "raw" / raw["sha256"]
                if digest(path.read_bytes()) != raw["sha256"]:
                    return None
            return record["value"]
        except (OSError, ValueError, KeyError, TypeError):
            return None

    def raw(self, content, source):
        sha = digest(content)
        folder = self.root / "raw"
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / sha
        if not path.exists() or digest(path.read_bytes()) != sha:
            fd, temp = tempfile.mkstemp(dir=folder)
            try:
                with os.fdopen(fd, "wb") as handle:
                    handle.write(content)
                os.replace(temp, path)
            finally:
                if os.path.exists(temp):
                    os.unlink(temp)
        return {"sha256": sha, "source": public_url(source), "bytes": len(content)}


def unavailable(provider, product, query, reason, *, access, resolution, temporal, state="unavailable", job_id=None):
    return {"status": "unavailable", "provider": provider, "reason": reason, "access_status": state,
        "product": product, "location": {"latitude": query["latitude"], "longitude": query["longitude"]},
        "period": {"start": query["start"], "end": query["end"]}, "spatial_resolution": resolution,
        "temporal_resolution": temporal, "series": {}, "summary": None, "cache_status": "not_available",
        "provenance": {"product": product, "access_method": access, "query": query, "job_id": job_id},
        "limitations": [reason, "No missing or delayed source value is replaced with zero or another provider."]}
