#!/usr/bin/python3

import subprocess
import sys


try:
    subprocess.call(["resize2fs", "/dev/mmcblk0p2"])
    with open("/home/ravinder/log/update.log", "a+") as file:
        file.write("update to v1.1 success")
    sys.exit(0)
except Exception as e:
    with open("/home/ravinder/log/update.log", "a+") as file:
        file.write("update to v1.1 error : cannot expand filesystem")
    sys.exit(1)
