#!/usr/bin/python3

import subprocess
import sys
import os


try:
    
    subprocess.call(["mkdir", "/home/ravinder/update_temp"])
    os.chdir("/home/ravinder/update_temp/")
    subprocess.call(["wget", "https://bnpd.nutech-integrasi.com/files/v2.2/v2.2.tar.xz", "-O", "/home/ravinder/update_temp/v2.2.tar.xz", "--backups=0"])
    subprocess.call(["tar", "-xf", "/home/ravinder/update_temp/v2.2.tar.xz", "-C", "/home/ravinder/update_temp"])
    subprocess.call(["cp", "-RT", "/home/ravinder/update_temp/v2.2_temp", "/usr/local/bin"])
    subprocess.call(["systemctl", "daemon-reload"])
    subprocess.call(['rm', '-rf', '/home/ravinder/update_temp'])

    with open("/home/ravinder/log/update.log", "a+") as file:
        file.write("update to v2.2 success\n")
    with open("/home/ravinder/ravinder-base/version", "w+") as f:
        f.write("2.2")
    os.chdir("/home/ravinder")
    subprocess.call(['shutdown', '-r', 'now'])
    sys.exit(0)
except Exception as e:
    with open("/home/ravinder/log/update.log", "a+") as file:
        file.write("update to v2.2 error : " + "(" +str(e)+ ")\n" )
    sys.exit(1)
