"""Prefetch an authentic historical subset; coordinates remain explicit.

Example: python -m next_season.environment.prefetch --latitude 25.7439
--longitude 89.2752 --start 2024-01-01 --end 2024-12-31
"""
import argparse
import json
from ..knowledge.identity import ROOT
from .power import PowerProvider

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--latitude",type=float,required=True)
    p.add_argument("--longitude",type=float,required=True)
    p.add_argument("--start",required=True)
    p.add_argument("--end",required=True)
    p.add_argument("--cache-dir",default=str(ROOT/".runtime/power"))
    args=p.parse_args()
    profile=PowerProvider(args.cache_dir).profile(args.latitude,args.longitude,args.start,args.end)
    print(json.dumps({key:profile[key] for key in ("provider","location","period","cache_status","coverage","response_sha256")},indent=2))
