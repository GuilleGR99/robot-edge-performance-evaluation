# -*- coding: utf-8 -*-

import rosbag
from collections import defaultdict
from io import BytesIO
import argparse
import math
import json
import os

parser = argparse.ArgumentParser(description="Rosbag analysis")
parser.add_argument("bag", help="Path to .bag file")
parser.add_argument("-v", "--verbose", action="store_true", help="Print table output")
args = parser.parse_args()

bag_path = args.bag
verbose = args.verbose

stats = defaultdict(lambda: {
    "count": 0,
    "bytes": 0,
    "times": []
})

bag = rosbag.Bag(bag_path)

start_time = bag.get_start_time()
end_time = bag.get_end_time()
duration = end_time - start_time

for topic, msg, t in bag.read_messages():
    stats[topic]["count"] += 1

    buff = BytesIO()
    msg.serialize(buff)
    stats[topic]["bytes"] += len(buff.getvalue())

    stats[topic]["times"].append(t.to_sec())

bag.close()

results = {}

if verbose:
    print("{:<50} {:>6} {:>10} {:>10} {:>10} {:>10} {:>10} {:>10}".format(
        "Topic", "Hz", "SizeKB", "BW", "PeakBW", "Jitter", "MinDt", "MaxDt"
    ))

for topic, data in stats.items():
    count = data["count"]
    total_bytes = data["bytes"]
    times = data["times"]

    if count == 0:
        continue

    freq = count / duration
    avg_size = total_bytes / count
    bw = total_bytes / duration

    jitter = 0
    min_dt = 0
    max_dt = 0
    peak_bw = 0

    if len(times) > 1:
        intervals = []
        inst_bw = []

        for i in range(1, len(times)):
            dt = times[i] - times[i-1]
            intervals.append(dt)

            if dt > 0:
                inst_bw.append(avg_size / dt)

        mean = sum(intervals) / len(intervals)
        var = sum((x - mean) ** 2 for x in intervals) / len(intervals)
        jitter = math.sqrt(var) * 1000

        min_dt = min(intervals) * 1000
        max_dt = max(intervals) * 1000

        if len(inst_bw) > 0:
            peak_bw = max(inst_bw)

    active_duration = 0
    if len(times) > 1:
        active_duration = times[-1] - times[0]

    results[topic] = {
        "frequency_hz": freq,
        "avg_size_kb": avg_size / 1024.0,
        "bandwidth_mb_s": bw / (1024.0 * 1024.0),
        "peak_bandwidth_mb_s": peak_bw / (1024.0 * 1024.0),
        "jitter_ms": jitter,
        "min_dt_ms": min_dt,
        "max_dt_ms": max_dt,
        "messages": count,
        "total_bytes": total_bytes,
        "active_duration_s": active_duration
    }

    if verbose:
        print("{:<50} {:6.2f} {:10.2f} {:10.2f} {:10.2f} {:10.2f} {:10.2f} {:10.2f}".format(
            topic,
            freq,
            avg_size / 1024.0,
            bw / (1024.0 * 1024.0),
            peak_bw / (1024.0 * 1024.0),
            jitter,
            min_dt,
            max_dt
        ))

# Save JSON
output_path = os.path.splitext(bag_path)[0] + "_analysis.json"

with open(output_path, "w") as f:
    json.dump({
        "bag": bag_path,
        "duration_s": duration,
        "topics": results
    }, f, indent=4)