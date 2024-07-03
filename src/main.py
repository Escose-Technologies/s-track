from datetime import datetime
import time
import psutil
import subprocess
import logging
import json

logging.basicConfig(filename='system_report.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

def get_system_info():
    system_info = {}

    # Get RAM information
    try:
        mem_info = psutil.virtual_memory()
        system_info["RAM_Info"] = {
            "Total": mem_info.total,
            "Available": mem_info.available,
            "Used": mem_info.used,
            "Free": mem_info.free
        }
    except Exception as e:
        logging.error(f"Failed to get RAM information: {e}")

    # Get Disk information
    try:
        disk_info = psutil.disk_partitions()
        disks = []
        for partition in disk_info:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                "Device": partition.device,
                "Mountpoint": partition.mountpoint,
                "Fstype": partition.fstype,
                "Total": usage.total,
                "Used": usage.used,
                "Free": usage.free,
                "Percentage": usage.percent
            })
        system_info["Disk_Info"] = disks
    except Exception as e:
        logging.error(f"Failed to get disk information: {e}")

    # Get CPU information
    try:
        cpu_info = {
            "Physical_Cores": psutil.cpu_count(logical=False),
            "Total_Cores": psutil.cpu_count(logical=True),
            "Max_Frequency": psutil.cpu_freq().max,
            "Min_Frequency": psutil.cpu_freq().min,
            "Current_Frequency": psutil.cpu_freq().current,
            "CPU_Usage": psutil.cpu_percent(interval=1)
        }
        system_info["CPU_Info"] = cpu_info
    except Exception as e:
        logging.error(f"Failed to get CPU information: {e}")

    # Get detailed system information using system_profiler
    try:
        system_profiler_data = subprocess.check_output(['system_profiler', 'SPHardwareDataType', 'SPStorageDataType', 'SPMemoryDataType', 'SPDisplaysDataType', 'SPNetworkDataType'], text=True)
        system_info["Detailed_System_Info"] = system_profiler_data
    except Exception as e:
        logging.error(f"Failed to get detailed system information: {e}")
    system_info["Installed_Applications"] = get_installed_applications()
    return system_info

def get_installed_applications():
    try:
        apps = subprocess.check_output(['mdfind', 'kMDItemKind="Application"'], text=True).splitlines()
        apps_info = []
        for app in apps:
            try:
                last_used_output = subprocess.check_output(['mdls', '-name', 'kMDItemLastUsedDate', app], text=True).strip()
                if "kMDItemLastUsedDate" in last_used_output:
                    last_used = last_used_output.split("=")[-1].strip().strip("\"")
                    last_used = datetime.strptime(last_used, "%Y-%m-%d %H:%M:%S %z")
                else:
                    last_used = "Never used"
                apps_info.append({
                    "Path": app,
                    "LastUsed": last_used
                })
            except Exception as e:
                logging.error(f"Failed to get last used time for app {app}: {e}")
                apps_info.append({
                    "Path": app,
                    "LastUsed": "Unknown"
                })
        return apps_info
    except Exception as e:
        logging.error(f"Failed to get installed applications: {e}")
        return []
if __name__ == "__main__":
    try:
        start_time = time.time()
        info = get_system_info()
        end_time = time.time()
        with open("system_report.json", "w") as report_file:
            json.dump(info, report_file, indent=4)
        logging.info("System report generated successfully.")
        logging.info(f"Total time taken to generate the report: {end_time - start_time} seconds")
    except Exception as e:
        logging.error(f"Failed to generate system report: {e}")
