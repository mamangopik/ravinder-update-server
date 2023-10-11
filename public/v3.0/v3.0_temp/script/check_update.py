#!/usr/bin/env python3
from urllib.request import urlopen, urlretrieve
from packaging.version import Version
import subprocess
import schedule
import socket
import time
import json


def update():
    current_version = ""
    with open('/home/ravinder/ravinder-base/version', 'r+') as f:
        ver = f.read()
        f.seek(0, 0)
        if not ver:
            f.write('1.0')
            f.seek(0, 0)
        current_version = f.readline()

    domain_server = "bnpd.nutech-integrasi.com"
    check_version_path = "ravinder-latest-version"
    update_path = "ravinder-update-path"
    need_update = False
    url_file = ""
    file_name = ""

    socket.setdefaulttimeout(15)
    try:
        response = urlopen(
            f"https://{domain_server}/{check_version_path}")
        data_json = json.loads(response.read())
    except Exception as e:
        raise e

    try:
        new_version = data_json["ravinder"]["version"]
        if Version(current_version) < Version(new_version):
            need_update = True
    except Exception as e:
        print("format error")

    if need_update:
        try:
            response = urlopen(f"https://{domain_server}/{update_path}")
            data_json = json.loads(response.read())
            url_file = data_json["script_link"]
            print(url_file)
            file_name = url_file.split('/')[-1]
            urlretrieve(url_file, f"/home/ravinder/{file_name}")
            ret = subprocess.run(
                ["chmod", "+x", f"/home/ravinder/{file_name}"]).returncode
            if not subprocess.run([f"/home/ravinder/./{file_name}"]).returncode:
                with open(f'/home/ravinder/ravinder-base/version', 'w+') as f:
                    f.write(new_version)
        except Exception as e:
            raise e


schedule.every(1).hours.do(update)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
