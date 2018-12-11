import argparse
import logging

from bokeh.server.server import Server
import numpy as np
from tornado.ioloop import PeriodicCallback, IOLoop
import pandas as pd
from caproto.threading.client import Context

from .event_builder import basic_event_builder, ebuild_mgr
from .plotters import (histogram_1d, w_histogram_1d, tmn_histogram_1d,
    triple_histogram_1d)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Bokeh live plotting utility")
    

    parser.add_argument("-b", action="store_true", help="TODO Use Browser")
    parser.add_argument("-p", action="store_true", help="TODO Broadcast PV")

    subparsers = parser.add_subparsers(dest="plot_op", help='sub-command help')

    # Basic 1d Histogram
    parser_hist = subparsers.add_parser(
        'hist', help='Use standard histogram')
    parser_hist.add_argument('pv', type=str, help='PV for histograming')
        
    # Weighted 1d Histogram
    parser_whist = subparsers.add_parser(
        'weight_hist', help='Use a weighted histogram')
    parser_whist.add_argument('pv', type=str, help='PV for hit locations')
    parser_whist.add_argument('weight', type=str, help='PV for hit weights')

    # Transmission 1d Histogram
    parser_tmnhist = subparsers.add_parser(
       'tmn_hist', help='Use a transmission histogram')
    parser_tmnhist.add_argument('pv', type=str, help='PV for hit locations')
    parser_tmnhist.add_argument('weight', type=str, help='PV for transmission weights')

    #parser_thist.add_argument(
    #    'incident', type=str, help='PV for incident weights')
    #parser_thist.add_argument(
    #    'out', type=str, help='PV for exiting weights')


    # All 3 1d Histogram
    parser_triphist = subparsers.add_parser(
       'trip_hist', help='Use a transmission histogram')
    parser_triphist.add_argument('pv', type=str, help='PV for hit locations')
    parser_triphist.add_argument('weight', type=str, help='PV for transmission weights')





    #parser.add_argument("operation",choices=['hist']) 
    #parser.add_argument("--first", nargs="?")
    #parser.add_argument("second", nargs="?")
    #parser.add_argument("-t", action="store_true")

    args = parser.parse_args()

    print(args)
    print(vars(args))

    #plot_type_lookup = {
    #    'hist': histogram_1d
    #}

    #plot_class = plot_type_lookup[args.plot_op]
    #a = histogram_1d(pv='beam_sim:x')
    
    if args.plot_op == "hist":
        plot_class = histogram_1d
        plot_obj = plot_class(pv=args.pv)

    if args.plot_op == "weight_hist":
        plot_class = w_histogram_1d
        plot_obj = plot_class(pv=args.pv, weight=args.weight)
    
    if args.plot_op == "tmn_hist":
        plot_class = tmn_histogram_1d
        plot_obj = plot_class(pv=args.pv, weight=args.weight)

    if args.plot_op == "trip_hist":
        plot_class = triple_histogram_1d
        plot_obj = plot_class(pv=args.pv, weight=args.weight)
    
    print("MAIN HAS RUN")

    server = Server(
        {
            '/go':plot_obj.draw_plot,
        },
        num_procs=1,
    )
    #server.start()
    plot_obj.start()
    print("#########################################################")
    # a = ebuild_mgr(pv_list = ['beam_sim:x','beam_sim:y','beam_sim:w'])
    # a.subscribe_all()

    #io_loop = IOLoop.current()
    io_loop = server.io_loop
    try:
        io_loop.start()
    except KeyboardInterrupt:
        print("terminating")
        io_loop.stop()
