import subprocess
import json
import re

graph = {}

nodes = subprocess.check_output(["rosnode", "list"]).decode().split()

for node in nodes:
    info = subprocess.check_output(["rosnode", "info", node]).decode()

    pubs = re.findall(r"Publications:\n((?:\s+\* .+\n)+)", info)
    subs = re.findall(r"Subscriptions:\n((?:\s+\* .+\n)+)", info)

    if pubs:
        for line in pubs[0].split("\n"):
            if "*" in line:
                topic = line.split("*")[1].strip().split(" ")[0]
                graph.setdefault(topic, {"publishers": [], "subscribers": []})
                graph[topic]["publishers"].append(node)

    if subs:
        for line in subs[0].split("\n"):
            if "*" in line:
                topic = line.split("*")[1].strip().split(" ")[0]
                graph.setdefault(topic, {"publishers": [], "subscribers": []})
                graph[topic]["subscribers"].append(node)

# Guardar
with open("node_topic_graph.json", "w") as f:
    json.dump(graph, f, indent=4)
