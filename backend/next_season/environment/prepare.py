"""Prepare real NASA source caches; resume asynchronous jobs without a worker queue."""
import argparse
import json
from pathlib import Path
import time
from ..knowledge.identity import ROOT
from .profile import EnvironmentalProfile


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--latitude",type=float,required=True)
    parser.add_argument("--longitude",type=float,required=True)
    parser.add_argument("--start",required=True)
    parser.add_argument("--end",required=True)
    parser.add_argument("--cache-root",type=Path,default=ROOT/".runtime")
    parser.add_argument("--attempts",type=int,default=1)
    args=parser.parse_args()
    if not 1<=args.attempts<=200:
        parser.error("Use 1–200 bounded attempts")
    provider=EnvironmentalProfile(args.cache_root)
    for attempt in range(args.attempts):
        profile=provider.profile(args.latitude,args.longitude,args.start,args.end)
        print(json.dumps({"attempt":attempt+1,"location":profile["location"],"provider_status":profile["provider_status"]}),flush=True)
        pending=any(value.get("access_status") in ("pending","collecting") for value in profile["provider_status"].values())
        if not pending or attempt+1==args.attempts:
            break
        time.sleep(2)


if __name__=="__main__":
    main()
