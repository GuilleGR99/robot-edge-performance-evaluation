#!/usr/bin/env python2

import subprocess
import psutil
import time
import json
import rospy


# -------------------------
# CONFIG
# -------------------------
NODES = [
    "/bag_recorder", "/gazebo", "/robot/amcl",
    "/robot/complementary_filter_node", "/robot/controller_spawner",
    "/robot/map_server", "/robot/move_base",
    "/robot/robot_state_publisher", "/robot/twist_marker",
    "/robot/twist_mux", "/rosout", "/rviz"
]

INTERVAL = 1.0
OUTPUT = "../data/node_metrics.json"


# -------------------------
def get_pid(node_name):
    try:
        result = subprocess.check_output(
            ["rosnode", "info", node_name],
            stderr=subprocess.STDOUT
        )

        for line in result.split("\n"):
            if "Pid" in line:
                return int(line.split(":")[1].strip())

    except:
        return None

    return None


# -------------------------
def get_usage(proc):
    try:
        cpu = proc.cpu_percent(interval=None)
        mem = proc.memory_info().rss

        for child in proc.children(recursive=True):
            cpu += child.cpu_percent(interval=None)
            mem += child.memory_info().rss

        return cpu, mem / (1024.0**2)

    except psutil.NoSuchProcess:
        return None, None


# -------------------------
def init_processes():
    processes = {}

    for node in NODES:
        pid = get_pid(node)
        if pid:
            processes[node] = psutil.Process(pid)
        else:
            print("[WARN] No PID for {}".format(node))

    return processes


# -------------------------
def monitor():
    processes = init_processes()
    data = []

    # warm-up
    for p in processes.values():
        p.cpu_percent(interval=None)

    no_nodes_counter = 0

    while not rospy.is_shutdown():
        time.sleep(INTERVAL)

        timestamp = rospy.Time.now().to_sec()
        alive_nodes = 0

        for node in list(processes.keys()):
            proc = processes[node]
            cpu, mem = get_usage(proc)

            if cpu is None:
                print("[INFO] {} murio, reintentando...".format(node))
                pid = get_pid(node)

                if pid:
                    processes[node] = psutil.Process(pid)
                    processes[node].cpu_percent(interval=None)
                    alive_nodes += 1
                else:
                    print("[INFO] {} eliminado del tracking".format(node))
                    del processes[node]

                continue

            alive_nodes += 1

            data.append({
                "time": timestamp,
                "node": node,
                "cpu_percent": cpu,
                "memory_mb": mem
            })

            print("{}: CPU={:.2f}% MEM={:.2f}MB".format(node, cpu, mem))

        with open(OUTPUT, "w") as f:
            json.dump(data, f, indent=2)

        if alive_nodes == 0:
            no_nodes_counter += 1
            print("[INFO] No hay nodos activos ({}/3)".format(no_nodes_counter))
        else:
            no_nodes_counter = 0

        if no_nodes_counter >= 3:
            print("[INFO] Confirmado: todos los nodos han terminado. Cerrando monitor.")
            break


# -------------------------
if __name__ == "__main__":
    rospy.init_node("ros_node_resource_monitor", anonymous=True)
    monitor()