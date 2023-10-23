#!/usr/bin/env python3

import logging
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter
import subprocess
import time
from subprocess import call
import subprocess
from subprocess import DEVNULL
import schedule
import sys
import dotenv


# Define the list of network interfaces to test
test_server = "8.8.8.8"

LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s:%(lineno)d"
MODEM_LOG_FILE = '/home/ravinder/log/modem.log'
modem_logger = logging.getLogger('modem_logging')
modem_logger.setLevel(logging.DEBUG)
modem_logger_file = TimedRotatingFileHandler(
    MODEM_LOG_FILE, when='D', interval=1, backupCount=3)
modem_logger_file.setLevel(logging.DEBUG)
modem_logger_file.setFormatter(Formatter(LOG_FORMAT))
modem_logger.addHandler(modem_logger_file)

try:
    server_config_file = dotenv.find_dotenv('/etc/config/server.conf')
    current_server_config = dotenv.dotenv_values(server_config_file)
except Exception as e:
    modem_logger.error(str(e))

try:
    from gpiozero import Buzzer
except Exception as e:
    modem_logger.error(str(e))


def resetModemPwr():
    modemRst = Buzzer(26)
    modem_logger.info("Hard Reset Modem")
    modemRst.on()
    time.sleep(3)
    modemRst.off()
    time.sleep(10)

def get_ping_metrics(interface):
    ping_result = subprocess.call(
        ["ping", "-I", interface, "-c", "4", "-q", test_server]
    )
    ping_result=str(ping_result)
    # print("Result",ping_result)
    RC = int(ping_result.split('\n')[-1])
    try:
        return RC
    except subprocess.CalledProcessError as e:
        # Handle errors, e.g., if ping fails
        return 2


def restart_service():
    modem_logger.info("restart service")
    time.sleep(10)
    sys.exit()

def init_modem():
    try:
        # subprocess.Popen("start-modem.sh", shell=True)
        call(['start-modem.sh'])
        modem_logger.info("Init Modem")
    except:
        modem_logger.error("Failed Init Modem")

def soft_reset_modem():
    status = [0,0]
    modem_logger.info('Soft Reset Modem')
    try:
        process=subprocess.Popen(["stop-modem.sh"], shell=False)
        time.sleep(60)
        if process.poll() is None:
            process.kill()
            modem_logger.warning('stop modem run too long,process terminated')
            modem_logger.error('Failed Stop Modem')
            status[0]=0
        else:
            modem_logger.info('stop modem')
            status[0]=1

        # call(['start-modem.sh'])
    except:
        modem_logger.error('Failed Stop Modem')
        status[0]=0

    time.sleep(3)

    try:
        process=subprocess.Popen(["start-modem.sh"], shell=False)
        time.sleep(90)
        if process.poll() is None:
            process.kill()
            modem_logger.warning('start modem run too long,process terminated')
            modem_logger.error('Failed start Modem')
            status[1]=0
        else:
            modem_logger.info('Start Modem success')
            status[1]=1

        # call(['start-modem.sh'])
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

def ping_ravinder_server():
    ping_result = subprocess.call(
        ["ping", "-c", "1", "-q", current_server_config["ADSB_SBS1_HOST"]]
    )
    ping_result=str(ping_result)
    # print("Result",ping_result)
    RC = int(ping_result.split('\n')[-1])
    try:
        return RC
    except subprocess.CalledProcessError as e:
        # Handle errors, e.g., if ping fails
        return 1

def main():
    init_modem()
    time.sleep(5)
    no_connection_cnt=0
    soft_reset_cnt = 0
    while 1:
        try:
            ping_server = ping_ravinder_server()
            if ping_server == 1:
                dotenv.set_key(server_config_file, "HAS_CONNECTION","False", quote_mode="never")
            else:
                dotenv.set_key(server_config_file, "HAS_CONNECTION","True", quote_mode="never")
        except:
            pass

        RC = get_ping_metrics("wwan0")
        # print("RC=",RC)
        if RC == 0:
            no_connection_cnt=0
            soft_reset_cnt = 0
            # modem_logger.info('got connection')
        elif RC == 1:
            no_connection_cnt +=1
        else:
            modem_logger.info('restart modem service')
            sys.exit()
        # jika 5x ping tidak ada koneksi internet
        if no_connection_cnt%5==0 and no_connection_cnt>0:
            # print("soft reset modem")
            soft_reset_modem()
            soft_reset_cnt += 1
            if soft_reset_cnt%3==0 and soft_reset_cnt>0:
                try:
                    resetModemPwr()
                    modem_logger.info('hard reset modem OK')
                    time.sleep(2)
                except:
                    modem_logger.error('failed to hard reset modem')
        time.sleep(1)


if __name__ == "__main__":
    modem_logger.info("Starting Script")
    main()
