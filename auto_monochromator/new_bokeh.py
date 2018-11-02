import argparse
import logging

from bokeh.server.server import Server
import numpy as np
from tornado.ioloop import PeriodicCallback, IOLoop
import pandas as pd
from caproto.threading.client import Context

from .event_builder import basic_event_builder
from .plotters import histogram_1d

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Bokeh live plotting utility")
    
    subparsers = parser.add_subparsers(dest="op", help='sub-command help')

    parser.add_argument("-b", action="store_true", help="TODO Use Browser")

    parser_hist = subparsers.add_parser('hist', help='Use standard histogram')
    
    parser_hist.add_argument(
        'pv', type=str, help='PV for histograming')

    parser_hist = subparsers.add_parser('dummy', help='Test use only')


    #parser.add_argument("operation",choices=['hist']) 
    #parser.add_argument("--first", nargs="?")
    #parser.add_argument("second", nargs="?")
    #parser.add_argument("-t", action="store_true")

    args = parser.parse_args()

    print(args)
    print(vars(args))
    
    
    
    exit()

    a = histogram_1d(pv='beam_sim:x')
    print("MAIN HAS RUN")

    server = Server(
        {
            '/go':a.draw_plot,
        },
        num_procs=1,
    )
    server.start()
    a.start()


    #io_loop = IOLoop.current()
    io_loop = server.io_loop
    try:
        io_loop.start()
    except KeyboardInterrupt:
        print("terminating")
        io_loop.stop()
