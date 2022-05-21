import time

import psutil
from flask import Blueprint, jsonify, request
from lib.system.utils import disk_usage, net_usage, sys_fans, sys_memory, temperatures

sys_api = Blueprint("sys", __name__, url_prefix="/sys")


@sys_api.route("/full", methods=["GET"])
def full():
    data = {}
    data["uptime"] = time.time() - psutil.boot_time()
    data["cpu"] = psutil.cpu_percent()
    data["mem"] = sys_memory()
    data["disks"] = disk_usage()
    data["temperatures"] = temperatures()
    data["fans"] = sys_fans()
    data["net_usage"] = net_usage()
    return (jsonify(data), 200)


@sys_api.route("/query", methods=["GET"])
def query_sys():
    data = {}
    for field in request.get_json():
        if field == "uptime":
            data["uptime"] = time.time() - psutil.boot_time()
        elif field == "cpu":
            data["cpu"] = psutil.cpu_percent()
        elif field == "mem":
            data["mem"] = sys_memory()
        elif field == "disks":
            data["disks"] = disk_usage()
        elif field == "uptime":
            data["temperatures"] = temperatures()
        elif field == "fans":
            data["fans"] = sys_fans()
        elif field == "net_usage":
            data["net_usage"] = net_usage()

    return (jsonify(data), 200)


@sys_api.route("/cpu", methods=["GET"])
def cpu_usage():
    return (jsonify(psutil.cpu_percent()), 200)


@sys_api.route("/ram", methods=["GET"])
def ram_usage():
    return (jsonify(sys_memory()), 200)


@sys_api.route("/uptime", methods=["GET"])
def uptime():
    return (jsonify(time.time() - psutil.boot_time()), 200)


@sys_api.route("/network", methods=["GET"])
def network():
    return (jsonify(net_usage()), 200)


@sys_api.route("/disks", methods=["GET"])
def disks():
    return (jsonify(disk_usage()), 200)


@sys_api.route("/temperatures", methods=["GET"])
def temp():
    return (jsonify(temperatures()), 200)


@sys_api.route("/fans", methods=["GET"])
def fans():
    return (jsonify(sys_fans()), 200)
