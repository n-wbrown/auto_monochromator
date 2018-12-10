from bokeh.layouts import column
from functools import partial
from collections import deque

import numpy as np
#from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.server.server import Server
#from bokeh.themes import Theme
#from bokeh.models import Button
from bokeh.palettes import RdYlBu3, grey
#from random import random
from tornado.ioloop import PeriodicCallback, IOLoop
#import time
import pandas as pd
#import socket
import logging

from caproto.threading.client import Context

from .event_builder import ebuild_mgr
from .rapid_stats import RapidHist, RapidWeightHist, RapidTransmissionHist 


logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

class plotter_template:
    def __init__(self, *args, **kwargs):
        
        self.make_plot_t = kwargs.get('make_plot_t', 500)
        self.add_data_t = kwargs.get('add_data_t', 500)
        # None should be changed when implemented 
        self.data = None
        self.make_plot = PeriodicCallback(
            self.make_plot_method,
            self.make_plot_t
        )
        self.add_data = PeriodicCallback(
            self.add_data_method,
            self.add_data_t
        )

    def start(self):
        self.make_plot.start()
        self.add_data.start()

    def add_data_method(self):
        """
        Implement 1st tier data aggregation here
        """
        raise NotImplementedError

    def make_plot_method(self):
        """
        Implement plot generation procedure here
        """
        raise NotImplementedError

    def draw_plot(self, doc):
        """
        Construct the Bokeh figure and plot here
        """
        def callback():
            """
            Implement the histogram ubdating feature here.
            """
            raise NotImplementedError
        raise NotImplementedError


class histogram_1d(plotter_template):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        
        self.maxlen = kwargs.get('maxlen',1000)
        self.data = RapidHist(maxlen=self.maxlen, minlen=1)
        self.data_cache = deque(maxlen=self.maxlen)
        self.datats_cache = deque(maxlen=self.maxlen)
        self.ebuild = ebuild_mgr(pv_list=[kwargs['pv']])
        self.ebuild.subscribe_all()

        self.ctx = Context()
        self.pv = kwargs['pv']

        # Connect to the PV
        [self.x_monitor] = self.ctx.get_pvs(self.pv)
        self.x_subscription = self.x_monitor.subscribe(data_type='time')
        try:
            self.x_token = self.x_subscription.add_callback(self.x_handler)
        except TimeoutError:
            logger.error("Failed to connect to PV")
            exit(1)
        
        self._hist_heights = []
        self._hist_bins = []

    def x_handler(self,response):
        #print("DATA:", response.data[0])
        #print("TS:", response.metadata.timestamp)
        self.data_cache.append(response.data[0])
        self.datats_cache.append(response.metadata.timestamp)


    def add_data_method(self):
        # self.data.push([list(self.data_cache)])
        # print(self.data_cache)
        # self.datat.push([list(self.datats_cache)])
        self.data.push([self.ebuild.get_data()['beam_sim:x'].values])
        # print(self.ebuild.get_data()['beam_sim:x'].values)
        self.data_cache.clear()
        self.datats_cache.clear()
        
    def make_plot_method(self):
        # print(self.ebuild.get_data()['beam_sim:x'].values)
        self._hist_heights, [self._hist_bins] = self.data.hist(bins=20)
 
    def draw_plot(self, doc):
        fig = figure()
        hist_plot = fig.quad(
            top=[0],
            bottom=[1],
            left=[0],
            right=[1],
            fill_color="#036564",
            line_color="#033649"
        )
        def callback():
            new_hist_data = dict()
            new_hist_data['top'] =  self._hist_heights 
            new_hist_data['bottom'] = np.zeros(len(self._hist_heights))
            new_hist_data['left'] = self._hist_bins[:-1]
            new_hist_data['right'] = self._hist_bins[1:]
            # Push the data to the plot 
            hist_plot.data_source.data = new_hist_data
            

        doc.add_periodic_callback(
            callback,
            500
        )
        
        doc.add_root(column([fig],sizing_mode='stretch_both'))

class w_histogram_1d(histogram_1d):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        
        self.data = RapidWeightHist(maxlen=self.maxlen)
        self.weight_cache = deque(maxlen=self.maxlen)
        self.weightts_cache = deque(maxlen=self.maxlen)
        
        # connect to the weight PV
        self.weight = kwargs['weight']
        [self.w_monitor] = self.ctx.get_pvs(self.weight)
        self.w_subscription = self.w_monitor.subscribe(data_type='time')
        try:
            self.x_token = self.x_subscription.add_callback(self.w_handler)
        except TimeoutError:
            logger.error("Failed to connect to PV")
            exit(1)
        self.data_block = None

    def w_handler(self, response):
        self.weight_cache.append(response.data[0])
        self.weightts_cache.append(response.metadata.timestamp)

    def add_data_method(self):
        #self.data.push([list(self.data_cache)])
        data_serires = pd.Series(
            list(self.data_cache),
            index=list(self.datats_cache))
        weights_serires = pd.Series(
            list(self.weight_cache),
            index=list(self.weightts_cache))


        self.data_cache.clear()
        self.datats_cache.clear()
        self.weight_cache.clear()
        self.weightts_cache.clear()
        
