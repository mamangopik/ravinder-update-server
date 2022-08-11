#!/usr/bin/python3

import subprocess
import sys


try:
    subprocess.call(["raspi-config ", "--expand-rootfs"])
    with open("/home/ravinder/log/update.log", "a+") as file:
        file.write("update to v1.1 success")
    with open("/home/ravinder-base/version", "w+") as f:
        f.write("1.1")
    subprocess.call(['shutdown', '-r', 'now'])
    sys.exit(0)
except Exception as e:
    with open("/home/ravinder/log/update.log", "a+") as file:
        file.write("update to v1.1 error : cannot expand filesystem")
    sys.exit(1)
