#!/usr/bin/python3

import subprocess
import sys
import os

try:
    
    subprocess.call(["mkdir", "/home/ravinder/update_temp"])
    os.chdir("/home/ravinder/update_temp/")
    subprocess.call(["wget", "http://hidayat-pc.local:6500/files/v3.0/v3.0.tar.xz", "-O", "/home/ravinder/update_temp/v3.0.tar.xz", "--backups=0"])
    subprocess.call(["tar", "-xf", "/home/ravinder/update_temp/v3.0.tar.xz", "-C", "/home/ravinder/update_temp"])
    subprocess.call(["cp", "-RT", "/home/ravinder/update_temp/v3.0_temp/script", "/usr/local/bin"])
    subprocess.call(["cp", "-RT", "/home/ravinder/update_temp/v3.0_temp/service", "/etc/systemd/system"])
    subprocess.call(["systemctl", "daemon-reload"])
    subprocess.call(["systemctl", "enable", "adsb_network_manager.service"])
    subprocess.call(['rm', '-rf', '/home/ravinder/update_temp'])

    with open("/home/ravinder/log/update.log", "a+") as file:
        file.write("update to v3.0 success\n")
    with open("/home/ravinder/ravinder-base/version", "w+") as f:
        f.write("3.0")
    os.chdir("/home/ravinder")
    subprocess.call(['shutdown', '-r', 'now'])
    sys.exit(0)
except Exception as e:
    with open("/home/ravinder/log/update.log", "a+") as file:
        file.write("update to v3.0 error : " + "(" +str(e)+ ")\n" )
    sys.exit(1)
