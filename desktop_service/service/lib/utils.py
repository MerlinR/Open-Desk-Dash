import psutil
import time
from pyroute2 import NDB


def get_def_interface() -> str:
    ip = NDB()
    if_name = ip.interfaces[ip.routes["default"]["oif"]]["ifname"]
    return if_name


def net_usage(inf=None) -> dict:
    if not inf:
        inf = get_def_interface()
    net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inf]
    net_in_1 = net_stat.bytes_recv
    net_out_1 = net_stat.bytes_sent
    time.sleep(1)
    net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inf]
    net_in_2 = net_stat.bytes_recv
    net_out_2 = net_stat.bytes_sent

    net_in = round((net_in_2 - net_in_1) / 1024 / 1024, 3)
    net_out = round((net_out_2 - net_out_1) / 1024 / 1024, 3)

    return {"in": net_in, "out": net_out}


def sys_memory() -> dict:
    data = {}
    v_mem = psutil.virtual_memory()
    data["total"] = v_mem.total
    data["used"] = v_mem.used
    data["perc"] = v_mem.percent
    return data


def disk_usage() -> dict:
    disks = {}
    for disk in psutil.disk_partitions():
        if "boot" in disk.mountpoint:
            continue
        disks[disk.mountpoint] = {
            k: v for k, v in psutil.disk_usage(disk.mountpoint)._asdict().items()
        }
    return disks


def tempetures() -> dict:
    data = {}
    temps = psutil.sensors_temperatures()
    data["cpu"] = temps["acpitz"][0].current
    for device, temp in temps.items():
        if "GPU" in device.upper():
            data["gpu"] = temp[0].current
    return data


def sys_fans() -> dict:
    data = {}
    for fan, speed in psutil.sensors_fans().items():
        if speed[0].label:
            data[fan] = speed[0].current
    return data
