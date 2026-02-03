import psutil
import platform
import socket

def get_system_info():
    """
    Returns basic details about the operating system and machine.
    """
    uname = platform.uname()
    info = (
        f"System: {uname.system} {uname.release}\n"
        f"Node Name: {uname.node}\n"
        f"Machine: {uname.machine}\n"
        f"Processor: {uname.processor}"
    )
    return info

def check_cpu():
    """
    Returns the current CPU usage percentage.
    """
    usage = psutil.cpu_percent(interval=1)
    return f"CPU Load: {usage}%"

def check_ram():
    """
    Returns the current Memory (RAM) usage stats.
    """
    mem = psutil.virtual_memory()
    total_gb = mem.total / (1024 ** 3) #converting bytes to gigabytes for readability
    available_gb = mem.available / (1024 ** 3)
    
    return (
        f"RAM Usage: {mem.percent}%\n"
        f"Total: {total_gb:.2f} GB\n"
        f"Available: {available_gb:.2f} GB"
    )
    
def check_disk():
    """
    Returns usage of the primary disk partition (C: drive).
    """
    disk = psutil.disk_usage('C:\\')
    free_gb = disk.free / (1024 ** 3)
    return (
        f"Disk Usage (C:): {disk.percent}%\n"
        f"Free Space: {free_gb:.2f} GB"
    )

tool_registry = {
    "get_system_info": get_system_info,
    "check_cpu": check_cpu,
    "check_ram": check_ram,
    "check_disk": check_disk
}