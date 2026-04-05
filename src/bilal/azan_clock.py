#!/usr/bin/env python

from zeroconf import IPVersion, Zeroconf
from bilal.azan_config import AzanConfig, AzanConfigLoader

from bilal.azan_loader import AzanLoader
from bilal.azan_loader_calc import CalcAzanLoader
from bilal.azan_loader_local import LocalAzanLoader
import bilal.azan_local_discovery as azan_local_discovery
from bilal.azan_player import AzanPlayer
from bilal.azan_scheduler import AzanScheduler

import logging
from logging import Logger
import logging.handlers
import sys
import signal

from bilal.command_server import CommandServer
from bilal.azan_args import calendar_path, azan_files, parse_args

LOG_FILENAME = 'azan_clock_log_file.log'

azan_scheduler: AzanScheduler
local_discovery: azan_local_discovery.LocalDiscovery
zeroconf : Zeroconf

def setup_app_logger():
    # Setup Rotating Logger
    app_logger: Logger = logging.getLogger('azan_clock_app')
    app_logger.setLevel(logging.DEBUG)

    # Add the log message handler to the logger
    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s][%(filename)s:%(lineno)s] %(message)s')
    log_handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=1000000, backupCount=5)
    log_handler.setLevel(logging.DEBUG)
    log_handler.setFormatter(formatter)
    handler.setFormatter(formatter)

    app_logger.addHandler(log_handler)
    app_logger.addHandler(handler)

    app_logger.info("Starting Azan Clock" )
    return app_logger

def main():
    parse_args()
    logger: Logger = setup_app_logger()
    logger.info("Started Bilal")

    local_discovery = azan_local_discovery.LocalDiscovery(logger)
    local_discovery.start()

    config_file_path = 'config.json'
    config_loader: AzanConfigLoader = AzanConfigLoader(config_file_path)
    config = config_loader.getConfig()

    azan_loader: AzanLoader = CalcAzanLoader(
        config_loader)

    config.azan_audio_files_dir = azan_files()
    config_loader.setConfig(config)

    azan_player: AzanPlayer = AzanPlayer(config_loader, logger)
    azan_scheduler = AzanScheduler(azan_player, azan_loader, logger)
    # start http server
    server = CommandServer(logger, azan_player, azan_scheduler, azan_loader, config_loader)
    azan_scheduler.schedule_next_azan()

    server.runBottle()

if __name__ == '__main__':
    main()

def signal_handler(sig, frame):
    azan_scheduler.stop()
    local_discovery.stop()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
