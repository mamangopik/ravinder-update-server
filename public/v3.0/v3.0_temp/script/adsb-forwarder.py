#!/usr/bin/env python3

import socket
import time
import logging
from logging import Formatter
from gpiozero import LED
from logging.handlers import TimedRotatingFileHandler
import dotenv

blue = LED(15)
blue.on()
server_config_file = dotenv.find_dotenv('/etc/config/server.conf')
current_server_config = dotenv.dotenv_values(server_config_file)


def setLogger():

    print(current_server_config["ADSB_SBS1_HOST"], flush=True)
    print(current_server_config["ADSB_SBS1_PORT"], flush=True)
    LOG_FORMAT = ("%(asctime)s %(levelname)s %(message)s")
    LOG_LEVEL = logging.DEBUG
    CONN_LOG_FILE = "/home/ravinder/log/connection.log"
    DATA_LOG_FILE = "/home/ravinder/log/data.log"
    
    # connection logger
    conn_logger = logging.getLogger('adsb_socket.connection')
    conn_logger.setLevel(LOG_LEVEL)
    conn_logger_file = TimedRotatingFileHandler(
        CONN_LOG_FILE, when='D', interval=1, backupCount=3)
    conn_logger_file.setLevel(LOG_LEVEL)
    conn_logger_file.setFormatter(Formatter(LOG_FORMAT))
    conn_logger.addHandler(conn_logger_file)

    # data logger
    data_logger = logging.getLogger('adsb_socket.data')
    data_logger.setLevel(LOG_LEVEL)
    data_logger_file = TimedRotatingFileHandler(
        DATA_LOG_FILE, when='D', interval=1, backupCount=3)
    data_logger_file.setLevel(LOG_LEVEL)
    data_logger_file.setFormatter(Formatter(LOG_FORMAT))
    data_logger.addHandler(data_logger_file)

    return conn_logger, data_logger


def main():
    data = None
    conn_logger, data_logger = setLogger()

    sock_local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock_local.setblocking(False)
    isConnLocal = False
    sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #sock_server.settimeout(5)
    sock_server.setblocking(False)
    isConnServer = False
    local_addr = ('localhost', 30003)
    server_addr = (current_server_config["ADSB_SBS1_HOST"], int(
        current_server_config["ADSB_SBS1_PORT"]), current_server_config['HAS_CONNECTION'])
    server_addr_host = (current_server_config["ADSB_SBS1_HOST"], int(
        current_server_config["ADSB_SBS1_PORT"]))
    while (server_addr[2] == "True"):
        #conn_logger.info("looper")
        blue.off()
        if not isConnLocal:
            if sock_local.connect_ex(local_addr):
                conn_logger.error("local not connected!")
                continue

            #conn_logger.info("local connected!")
            isConnLocal = True
        try:
            data = sock_local.recv(4096)
            #print(repr(data) + "debug")
        except Exception as e:
            print(repr(e), flush=True)

        if not data:
            sock_local.close()
            sock_local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            isConnLocal = False
            continue
        else:
            # data_logger.info(data.decode('utf-8'))
            if not isConnServer:
                if sock_server.connect_ex(server_addr_host):
                    conn_logger.error("server not connected!")
                    # time.sleep(3)
                    continue
                #conn_logger.info("server connected!")
                isConnServer = True

            try:
                blue.on()
                sock_server.sendall(data)
                #data_logger.info(data.decode('utf-8'))
            except:
                sock_server.close()
                sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                isConnServer = False


if __name__ == "__main__":
    main()
