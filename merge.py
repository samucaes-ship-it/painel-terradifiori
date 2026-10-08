"""Merge a Meta ads_get_dataset_stats response (aggregation=event, WEB_ONLY) into data.json.
Usage: python3 merge.py <stats.json> <data.json>
Days are in America/Sao_Paulo. Days covered by the new response replace the stored ones."""
import json, sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
TZ = ZoneInfo("America/Sao_Paulo")
stats = json.load(open(sys.argv[1]))
try:
    data = json.load(open(sys.argv[2]))
except Exception:
    data = {"days": {}}
fresh = {}
for s in stats.get("stats", []):
    d = datetime.strptime(s["timestamp"], "%Y-%m-%dT%H:%M:%S%z").astimezone(TZ).strftime("%Y-%m-%d")
    day = fresh.setdefault(d, {})
    for e in s.get("data", []):
        day[e["value"]] = day.get(e["value"], 0) + int(e["count"])
start = datetime.strptime(stats["start_time"], "%Y-%m-%dT%H:%M:%S%z").astimezone(TZ)
first_full = start.strftime("%Y-%m-%d") if start.hour == 0 else None
for d, v in fresh.items():
    if d == min(fresh) and first_full is None and d in data["days"]:
        continue  # partial first day of the window: keep the stored total
    data["days"][d] = v
data["days"] = dict(sorted(data["days"].items()))
data["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
json.dump(data, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
print(len(data["days"]), "dias;", data["updated_at"])
