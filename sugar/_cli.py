"""
CLI module
"""

import logging
import os
import sys

import sugar

try:
    LOGGING = os.environ['LOGGING']
except KeyError:
    LOGGING = "INFO"

try:
    PORT = os.environ['PORT']
except KeyError:
    PORT = 9999

try:
    WORKERS = os.environ['WORKERS']
except KeyError:
    WORKERS = 8


def main():
    """
    Main function
    """
    log_format = "%(asctime)s %(levelname)-8s %(message)s"
    logging.basicConfig(format=log_format, stream=sys.stderr, level=LOGGING)
    server = sugar.Server(WORKERS, PORT)
    server.serve()
