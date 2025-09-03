import psutil
import platform
from datetime import datetime

from .get_uptime import get_uptime
from .format_bytes import format_bytes


def get_system_info() -> dict:
    """Get comprehensive system information"""
    # CPU Information
    cpu_info = {
        "usage_percent": round(psutil.cpu_percent(interval=1), 1),
        "cores": psutil.cpu_count(logical=False),
        "threads": psutil.cpu_count(logical=True),
        "frequency": None,
        "load_avg": None,
    }

    # Get CPU frequency if available
    try:
        freq = psutil.cpu_freq()
        if freq:
            cpu_info["frequency"] = {
                "current": round(freq.current, 2),
                "min": round(freq.min, 2),
                "max": round(freq.max, 2),
            }
    except:
        pass

    # Get load average if available (Unix systems)
    try:
        if hasattr(psutil, "getloadavg"):
            load_avg = psutil.getloadavg()
            cpu_info["load_avg"] = [round(x, 2) for x in load_avg]
    except:
        pass

    # Memory Information
    ram = psutil.virtual_memory()
    ram_info = {
        "total": round(ram.total / (1024**3), 2),
        "used": round(ram.used / (1024**3), 2),
        "available": round(ram.available / (1024**3), 2),
        "percent": round(ram.percent, 1),
        "free": round(ram.free / (1024**3), 2),
    }

    # Swap Information
    swap = psutil.swap_memory()
    swap_info = {
        "total": round(swap.total / (1024**3), 2),
        "used": round(swap.used / (1024**3), 2),
        "free": round(swap.free / (1024**3), 2),
        "percent": round(swap.percent, 1),
    }

    # Storage Information
    storage = []
    try:
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                storage.append(
                    {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": round(usage.total / (1024**3), 2),
                        "used": round(usage.used / (1024**3), 2),
                        "free": round(usage.free / (1024**3), 2),
                        "percent": round((usage.used / usage.total) * 100, 1),
                    }
                )
            except PermissionError:
                continue
    except:
        pass

    # Network Information
    network = []
    try:
        net_io = psutil.net_io_counters(pernic=True)
        for interface, stats in net_io.items():
            if stats.bytes_sent > 0 or stats.bytes_recv > 0:
                network.append(
                    {
                        "interface": interface,
                        "bytes_sent": stats.bytes_sent,
                        "bytes_recv": stats.bytes_recv,
                        "packets_sent": stats.packets_sent,
                        "packets_recv": stats.packets_recv,
                        "sent_readable": format_bytes(stats.bytes_sent),
                        "recv_readable": format_bytes(stats.bytes_recv),
                    }
                )
    except:
        pass

    # System Information
    system_info = {
        "os": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "hostname": platform.node(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor() or "Unknown",
        "uptime": get_uptime(),
        "python_version": platform.python_version(),
    }

    # Process Information (top processes by CPU usage)
    processes = []
    try:
        for proc in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_percent"]
        ):
            try:
                proc_info = proc.info
                if proc_info["cpu_percent"] > 0:
                    processes.append(
                        {
                            "pid": proc_info["pid"],
                            "name": proc_info["name"],
                            "cpu_percent": round(proc_info["cpu_percent"], 1),
                            "memory_percent": round(proc_info["memory_percent"], 1),
                        }
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Sort by CPU usage and get top 10
        processes = sorted(processes, key=lambda x: x["cpu_percent"], reverse=True)[:10]
    except:
        pass

    return {
        "cpu": cpu_info,
        "ram": ram_info,
        "swap": swap_info,
        "storage": storage,
        "network": network,
        "system": system_info,
        "processes": processes,
        "timestamp": datetime.now().isoformat(),
    }
