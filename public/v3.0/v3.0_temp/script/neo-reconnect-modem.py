#!/usr/bin/env python3

import logging
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter
import subprocess
import time
from subprocess import call
from subprocess import DEVNULL
import schedule
import sys
import dotenv

# from gpiozero import Buzzer

# Define the list of network interfaces to test
interfaces = ["wwan0","wlo1","eno1"]
test_server = "8.8.8.8"
ping_result = {}

LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s:%(lineno)d"
MODEM_LOG_FILE = '/home/hidayat/log/modem.log'
modem_logger = logging.getLogger('modem_logging')
modem_logger.setLevel(logging.DEBUG)
modem_logger_file = TimedRotatingFileHandler(
    MODEM_LOG_FILE, when='D', interval=1, backupCount=3)
modem_logger_file.setLevel(logging.DEBUG)
modem_logger_file.setFormatter(Formatter(LOG_FORMAT))
modem_logger.addHandler(modem_logger_file)


# def resetModemPwr():
#     modemRst = Buzzer(26)
#     modem_logger.info("Hard Reset Modem")
#     modemRst.on()
#     time.sleep(3)
#     modemRst.off()
#     time.sleep(10)

def get_ping_metrics(interface):
    ping_result = subprocess.call(
        ["ping", "-I", interface, "-c", "4", "-q", test_server]
    )
    ping_result=str(ping_result)
    print("Result",ping_result)
    RC = int(ping_result.split('\n')[-1])
    try:
        return RC
    except subprocess.CalledProcessError as e:
        # Handle errors, e.g., if ping fa3.ils
        return None, None


def restart_service():
    modem_logger.info("restart service")
    sys.exit()
def init_modem():
    try:
        call(['start-modem.sh'])
        modem_logger.info("Init Modem")
    except:
        modem_logger.error("Failed Init Modem")
        modem_logger

def soft_reset_modem():
    status = [0,0]
    modem_logger.info('Soft Reset Modem')
    try:
        call(['stop-modem.sh'])
        modem_logger.info('stop modem')
        status[0]=1
    except:
        modem_logger.error('Failed Stop Modem')
        status[0]=0

    time.sleep(3)

    try:
        call(['start-modem.sh'])
        modem_logger.info('Start Modem')
        status[1]=1
        time.sleep(5)
    except:
        modem_logger.error('Failed start Modem')
        status[1]=0

    if status[0]==1 and status[1]==1:
        modem_logger.info('restart modem success')
    elif status[0]==1 and status[1]==0:
        modem_logger.error('restart modem failed and modem stoped now')
    else:
        modem_logger.error('restart modem failed')



def main():
    while 1:
        for interface in interfaces:
            print(f"============{interface}==============")
            RC = get_ping_metrics(interface)
            print("RC=",RC)
            print(f"============{interface}==============\n\n")   
        time.sleep(3)


if __name__ == "__main__":
    modem_logger.info("Starting Script")
    main()
