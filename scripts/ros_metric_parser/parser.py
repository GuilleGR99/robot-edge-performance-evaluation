from pathlib import Path
import argparse
import re
import json

parser = argparse.ArgumentParser()
parser.add_argument(
    "--input", default="/home/summitxlq/.ros/log/latest", help="Directorio de logs"
)
parser.add_argument("--output", required=True, help="Ruta del archivo JSON de salida")

args = parser.parse_args()

directory = Path(args.input)
output_path = Path(args.output)

re_file = re.compile(r"^(bw|hz|delay).*stdout\.log$")
re_topic = re.compile(r"subscribed to \[(.+)\]")
re_avg = re.compile(r"average(?: (?:rate|delay))?:\s*([\d.]+)", re.IGNORECASE)
re_mean = re.compile(r"mean:\s*(-?[\d.]+)([a-zA-Z/]+)?", re.IGNORECASE)
re_std_dev = re.compile(r"std dev:\s*(-?[\d.]+)([a-zA-Z/]+)?", re.IGNORECASE)
re_min = re.compile(r"min:\s*(-?[\d.]+)([a-zA-Z/]+)?", re.IGNORECASE)
re_max = re.compile(r"max:\s*(-?[\d.]+)([a-zA-Z/]+)?", re.IGNORECASE)
re_window = re.compile(r"window:\s*(\d+)", re.IGNORECASE)

stdout_files = [f for f in directory.iterdir() if f.is_file() and re_file.match(f.name)]

data = []

for file in stdout_files:

    match = re_file.match(file.name)
    metric = match.group(1) if match else "unknown"

    with file.open("r", encoding="utf-8", errors="ignore") as f:
        topic = None
        avg = None
        mean = None
        mean_unit = None
        std_dev = None
        std_dev_unit = None
        min_unit = None
        min_ = None
        max_ = None
        max_unit = None
        window = None

        for line in f:
            line = line.strip()

            if "no new messages" in line:
                continue

            match = re_topic.search(line)
            if match:
                topic = match.group(1)
            match = re_avg.search(line)
            if match:
                avg = match.group(1)
            match = re_mean.search(line)
            if match:
                mean, mean_unit = match.groups()
            match = re_std_dev.search(line)
            if match:
                std_dev, std_dev_unit = match.groups()
            match = re_min.search(line)
            if match:
                min_, min_unit = match.groups()
            match = re_max.search(line)
            if match:
                max_, max_unit = match.groups()
            match = re_window.search(line)
            if match:
                window = match.group(1)
                if all(
                    [
                        topic,
                        avg is not None,
                        (
                            (metric == "bw" and mean is not None)
                            or (metric in ["delay", "hz"] and std_dev is not None)
                        ),
                        min_ is not None,
                        max_ is not None,
                    ]
                ):

                    data.append(
                        {
                            "file": file.name,
                            "topic": topic,
                            "metric": metric,
                            "average": float(avg),
                            "mean": float(mean) if mean is not None else None,
                            "mean_unit": mean_unit,
                            "std_dev": float(std_dev) if std_dev is not None else None,
                            "std_dev_unit": std_dev_unit,
                            "min": float(min_),
                            "min_unit": min_unit,
                            "max": float(max_),
                            "max_unit": max_unit,
                            "window": int(window),
                        }
                    )

                else:
                    print(f"[WARN] {file.name} | topic={topic} avg={avg} mean={mean} std={std_dev}")

                avg = None
                mean = None
                mean_unit = None
                std_dev = None
                std_dev_unit = None
                min_unit = None
                min_ = None
                max_ = None
                max_unit = None
                window = None


with open(output_path, "w") as f:
    json.dump(data, f, indent=2)
