from pathlib import Path
import argparse
import re
import json

parser = argparse.ArgumentParser()
parser.add_argument("--input", default="/home/summitxlq/.ros/log/latest", help="Directorio de logs")
parser.add_argument("--output", required=True, help="Ruta del archivo JSON de salida")

args = parser.parse_args()

directory = Path(args.input)
output_path = Path(args.output)

re_file = re.compile(r"(bw|hz|delay).*stdout\.log$")
re_topic = re.compile(r"subscribed to \[(.+)\]")
re_avg = re.compile(r"average:\s*([\d.]+)MB/s")
re_stats = re.compile(
    r"mean:\s*([\d.]+)MB\s*min:\s*([\d.]+)MB\s*max:\s*([\d.]+)MB\s*window:\s*(\d+)"
)
stdout_files = [f for f in directory.iterdir() if f.is_file() and re_file.match(f.name)]

data =[]

for file in stdout_files:
    with file.open("r", encoding="utf-8", errors="ignore") as f:
        topic = None
        avg = None
        mean = None
        min_ = None
        max_ = None
        window = None

        for line in f:
            line = line.strip()

            match = re_topic.search(line)
            if match:
                topic = match.group(1)
            match = re_avg.search(line)    
            if match:
                avg = float(match.group(1))
            match = re_stats.search(line)
            if match:
                mean, min_, max_, window = [float(stat) for stat in match.groups()]

                # la fila se guardara solo en caso de que haya datos estadisticos
                data.append({
                    "file": file.name,
                    "topic": topic,
                    "average_MBps": avg,
                    "mean_MB": mean,
                    "min_MB": min_,
                    "max_MB": max_,
                    "window": int(window)
                })

with open(output_path, "w") as f:
    json.dump(data, f, indent=2)