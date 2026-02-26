import psutil
import platform
import socket
import subprocess

def get_system_info():
    """
    Returns basic details about the operating system and machine.
    """
    uname = platform.uname()
    info = (
        f"System: {uname.system} {uname.release}\n"
        f"Node Name: {uname.node}\n"
        f"Machine: {uname.machine}\n"
        f"Processor: {uname.processor}\n"
        f"Version: {uname.version}"
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

def check_ddrive():
    """
    Returns usage of the D:Drive
    """
    disk = psutil.disk_usage('D:\\')
    free_gb = disk.free / (1024 ** 3)
    return (
        f"Disk Usage (D:): {disk.percent}%\n"
        f"Free Space: {free_gb:.2f} GB"
    )
    
def check_top_processes():
    """
    Returns the top 5 processes consuming the most RAM.
    """
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    top_5 = sorted(processes, key=lambda p: p['memory_info'].rss, reverse=True)[:5]
    
    result = "Top 5 Memory Hogs:\n"
    for p in top_5:
        mem_mb = p['memory_info'].rss / (1024 * 1024) # Convert to MB
        result += f"- {p['name']} (PID: {p['pid']}): {mem_mb:.2f} MB\n"
        
    return result

def check_internet():
    """
    Checks internet connectivity by pinging Google.
    """
    # Detect OS to select correct ping flag
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    
    try:
        output = subprocess.check_output(["ping", param, "1", "8.8.8.8"], text=True)
        
        if "TTL=" in output or "ttl=" in output:
            return "Internet is ONLINE. Ping successful."
        else:
            return "Internet seems unstable (Packet loss)."
            
    except subprocess.CalledProcessError:
        return "Internet is OFFLINE. Ping failed."

tool_registry = {
    "get_system_info": get_system_info,
    "check_cpu": check_cpu,
    "check_ram": check_ram,
    "check_disk": check_disk,
    "check_ddrive": check_ddrive,
    "check_top_processes":check_top_processes,
    "check_internet":check_internet
}
