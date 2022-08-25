#!/usr/bin/python3

import subprocess
import sys


try:
    subprocess.call(["raspi-config", "--expand-rootfs"])
    with open("/home/ravinder/log/update.log", "a+") as file:
        file.write("update to v1.1 success\n")
    with open("/home/ravinder/ravinder-base/version", "w+") as f:
        f.write("1.1")
    subprocess.call(['shutdown', '-r', 'now'])
    sys.exit(0)
except Exception as e:
    with open("/home/ravinder/log/update.log", "a+") as file:
        file.write("update to v1.1 error : cannot expand filesystem " + "(" +str(e)+ ")\n" )
    sys.exit(1)
