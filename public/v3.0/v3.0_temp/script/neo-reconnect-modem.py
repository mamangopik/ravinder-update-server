#!/usr/bin/env python3

import logging
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter
import subprocess
import time
from subprocess import call
from subprocess import DEVNULL
from gpiozero import Buzzer
import schedule
import sys
import dotenv

LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s:%(lineno)d"
MODEM_LOG_FILE = '/home/ravinder/log/modem.log'
modem_logger = logging.getLogger('modem_logging')
modem_logger.setLevel(logging.DEBUG)
modem_logger_file = TimedRotatingFileHandler(
    MODEM_LOG_FILE, when='D', interval=1, backupCount=3)
modem_logger_file.setLevel(logging.DEBUG)
modem_logger_file.setFormatter(Formatter(LOG_FORMAT))
modem_logger.addHandler(modem_logger_file)

server_config_file = dotenv.find_dotenv('/etc/config/server.conf')
current_server_config = dotenv.dotenv_values(server_config_file)


def ping():
    pingRc = call(['ping', '-I', 'wwan0', '-c1', '-w10', '-s0', '8.8.8.8'], stdout=DEVNULL, stderr=DEVNULL)
    pingServer = call(['ping', '-c1', '-w10', '-s0', current_server_config["ADSB_SBS1_HOST"]], stdout=DEVNULL, stderr=DEVNULL)
    return pingRc, pingServer


def resetModemPwr():
    modemRst = Buzzer(26)
    modem_logger.info("Hard Reset Modem")
    modemRst.on()
    time.sleep(3)
    modemRst.off()
    time.sleep(10)


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

#schedule.every(5).minutes.do(restart_service)


def main():
    failCount = 0
    afterDown = False

    time.sleep(3)

    while True:
        rc = ping()
        if(rc[1]):
            dotenv.set_key(server_config_file, "HAS_CONNECTION",
                           "False", quote_mode="never")
        else:
            dotenv.set_key(server_config_file, "HAS_CONNECTION",
                "True", quote_mode="never")

        # if ping no response success after 10s
        if rc[0]:
            if failCount < 7:
                failCount += 1
                modem_logger.info('Connection Down')
                soft_reset_modem()
            else:
                pass
        else:
            failCount = 0


        time.sleep(10)


if __name__ == "__main__":
    modem_logger.info("Starting Script")
    main()
