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
    pingRc = call(['ping', '-I', 'wwan0', '-c1', '-w10', '-s0', '8.8.8.8'])
    pingServer = call(['ping', '-c1', '-w10', '-s0', current_server_config["ADSB_SBS1_HOST"]])
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


#schedule.every(5).minutes.do(restart_service)


def main():
    
    failCount = 0
    afterDown = False
    try:
        call(['start-modem.sh'], stdout=DEVNULL, stderr=DEVNULL)
        modem_logger.info("Init Modem")
    except:
        modem_logger.error("Failed Init Modem")
        modem_logger

    time.sleep(3)

    while True:
        rc = ping()
        if(rc[1]):
            print(rc[1])
            dotenv.set_key(server_config_file, "HAS_CONNECTION",
                           "False", quote_mode="never")
            # subprocess.run(["systemctl", "restart", "openfortivpn.service"])
        else:
            dotenv.set_key(server_config_file, "HAS_CONNECTION",
                "True", quote_mode="never")

        # if ping no response success after 10s
        if rc[0]:
            print(rc)
            if failCount < 7:
                failCount += 1
                modem_logger.info('Connection Down')
                try:
                    call(['stop-modem.sh'], stdout=DEVNULL, stderr=DEVNULL)
                    modem_logger.info('Soft Reset Modem')
                    if not (failCount % 3):
                        resetModemPwr()
                except:
                    modem_logger.error('Failed Stop Modem')

                time.sleep(3)
                try:
                    # call(['start-modem.sh'], stdout=DEVNULL, stderr=DEVNULL)
                    call(['start-modem.sh'], stdout=DEVNULL, stderr=DEVNULL)
                    modem_logger.info('Start Modem')
                    time.sleep(5)
                    # continue
                except:
                    modem_logger.error('Failed Stop Modem')
            else:
                #schedule.run_pending()
                pass
        # ping succes
        else:
            failCount = 0

            # wait 10s before check connection again
        time.sleep(5)


if __name__ == "__main__":
    modem_logger.info("Starting Script")
    main()
