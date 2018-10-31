from bokeh.layouts import column
#from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.server.server import Server
#from bokeh.themes import Theme
#from bokeh.models import Button
from bokeh.palettes import RdYlBu3, grey
#from random import random
from functools import partial
from collections import deque
import numpy as np
from tornado.ioloop import PeriodicCallback, IOLoop
#import time
import pandas as pd
#import socket
import logging

from auto_monochromator.event_builder import basic_event_builder

from caproto.threading.client import Context

from types import SimpleNamespace

from .plotters import histogram_1d

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)





def main():
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
