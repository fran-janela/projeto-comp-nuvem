#main app that recives --debug and --verbose flags and read a ^C to configure exit

import sys
import signal
import argparse
import logging
import logging.handlers
import time
import os
import subprocess
import threading
import queue
import json
import configurate

#global variables
debug = False
verbose = False
config = {}

#logging
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#file handler
fh = logging.handlers.RotatingFileHandler('main.log', maxBytes=1000000, backupCount=5)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)
#console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

#signal handler
def signal_handler(sig, frame):
    logger.info('You pressed Ctrl+C!')
    logger.info('Configuring exit...')
    configurate.write_json(config)
    logger.info('Exit configured!')
    sys.exit(0)

#thread to read a ^C
def read_signal():
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()