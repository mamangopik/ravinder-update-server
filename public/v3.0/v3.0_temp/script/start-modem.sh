#!/bin/bash

qmicli -d /dev/cdc-wdm0 --dms-set-operating-mode='online'

echo ${APN}

ip link set wwan0 down
sleep 2
echo 'Y' | tee /sys/class/net/wwan0/qmi/raw_ip
sleep 5
ip link set wwan0 up
#qmi-network-raw /dev/cdc-wdm0 start
qmicli -p -d /dev/cdc-wdm0 --device-open-net='net-raw-ip|net-no-qos-header' --wds-start-network="apn='${APN}',username='${APN_USER}',password='${APN_PASS}',ip-type=4" --client-no-release-cid

udhcpc -q -n -i wwan0
