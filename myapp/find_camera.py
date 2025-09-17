#!/usr/bin/env python3
import argparse
# catch error if pyudev is not installed
try:
    import pyudev
except ImportError:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    print(f"{BOLD}{RED}*** This script requires the pyudev module. ***{RESET}")
    print("Type:")
    print("source /axelera/voyager-sdk/venv/bin/activate")
    print("and then rerun. If it still fails, install pyudev with:")
    print("pip install pyudev")
    exit(1)

def find_camera(searchname="HD Pro"):
    nodelist = [] 
    ctx = pyudev.Context()
    for dev in ctx.list_devices(subsystem="video4linux"):
        node = dev.device_node  # e.g., /dev/video0
        name = dev.properties.get("ID_V4L_PRODUCT") or dev.properties.get("NAME") or ""
        if searchname and searchname not in name:
            continue
        nodelist.append(node)
    if len(nodelist) == 0:
        return -1
    # return the number after "/dev/video" for the first found device
    return int(nodelist[0].replace("/dev/video", ""))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--searchname", help="e.g. 'HD Pro'")
    args = p.parse_args()
    searchname = args.searchname if args.searchname else "HD Pro"
    camnum = find_camera(searchname)
    if camnum < 0:
        print(f"Camera with name containing '{searchname}' not found")
    else:
        print(f"Camera '{searchname}' found at /dev/video{camnum}")

if __name__ == "__main__":
    main()
