from functools import partial
from collections import deque

import numpy as np
from bokeh.plotting import figure
from bokeh.layouts import column, gridplot
from bokeh.server.server import Server
from bokeh.palettes import RdYlBu3, grey
from tornado.ioloop import PeriodicCallback, IOLoop
import pandas as pd
import logging

from caproto.threading.client import Context

from .event_builder import ebuild_mgr
from .rapid_stats import (RapidHist, RapidWeightHist, 
    RapidTransmissionHist, InsufficientDataException)


logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

class plotter_template:
    def __init__(self, *args, **kwargs):

        self.maxlen = kwargs.get('maxlen',1000)

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


class histogram_1d_template(plotter_template):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._hist_heights = []
        self._hist_bins = []

    def make_plot_method(self):
        try:
            self._hist_heights, [self._hist_bins] = self.data.hist(bins=20)
        except InsufficientDataException:
            pass
 
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


class histogram_1d(histogram_1d_template):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        
        self.data = RapidHist(maxlen=self.maxlen, minlen=1)
        self.pv = kwargs['pv']

        self.ebuild = ebuild_mgr(pv_list=[self.pv],maxlen=self.maxlen)
        self.ebuild.subscribe_all()

    def add_data_method(self):
        self.data.push([self.ebuild.get_data()[self.pv].values])
        

class w_histogram_1d(histogram_1d_template):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        
        self.data = RapidWeightHist(maxlen=self.maxlen)
        self.pv = kwargs['pv']
        self.weight = kwargs['weight']

        self.ebuild = ebuild_mgr(pv_list=[self.pv, self.weight],maxlen=self.maxlen)
        self.ebuild.subscribe_all()

    def add_data_method(self):
        data_package = self.ebuild.get_data()
        self.data.push(
            data = [data_package[self.pv].values],
            weights = data_package[self.weight].values    
        )


class tmn_histogram_1d(histogram_1d_template):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        
        self.data = RapidTransmissionHist(maxlen=self.maxlen)
        self.pv = kwargs['pv']
        self.weight = kwargs['weight']

        self.ebuild = ebuild_mgr(pv_list=[self.pv, self.weight],maxlen=self.maxlen)
        self.ebuild.subscribe_all()

    def add_data_method(self):
        data_package = self.ebuild.get_data()
        self.data.push(
            data = [data_package[self.pv].values],
            weights = data_package[self.weight].values    
        )

    def make_plot_method(self):
        try:
            _, _, self._hist_heights, [self._hist_bins] = self.data.hist(bins=20)
        except InsufficientDataException:
            pass

class triple_histogram_1d(tmn_histogram_1d):
    def __init__(self,*args,**kwargs):
        # print("ARGS: ", args)
        # print("KWARGS:", kwargs)
        super().__init__(*args,**kwargs)
        self._hist_heights = []
        self._hist_bins = []
        self._w_hist_heights = []
        self._tmn_hist_heights = []

    def make_plot_method(self):
        try:
            self._hist_heights, self._w_hist_heights, self._tmn_hist_heights, [self._hist_bins] = self.data.hist(bins=20)
        except InsufficientDataException:
            pass

    def draw_plot(self, doc):
        fig = figure()
        w_fig = figure(x_range=fig.x_range)
        tmn_fig = figure(x_range=fig.x_range)
        hist_plot = fig.quad(
            top=[0],
            bottom=[1],
            left=[0],
            right=[1],
            fill_color="#036564",
            line_color="#033649"
        )
        w_hist_plot = w_fig.quad(
            top=[0],
            bottom=[1],
            left=[0],
            right=[1],
            fill_color="#036564",
            line_color="#033649"
        )
        tmn_hist_plot = tmn_fig.quad(
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

            w_new_hist_data = dict()
            w_new_hist_data['top'] =  self._w_hist_heights 
            w_new_hist_data['bottom'] = np.zeros(len(self._w_hist_heights))
            w_new_hist_data['left'] = self._hist_bins[:-1]
            w_new_hist_data['right'] = self._hist_bins[1:]
            # Push the data to the plot 
            w_hist_plot.data_source.data = w_new_hist_data

            tmn_new_hist_data = dict()
            tmn_new_hist_data['top'] =  self._tmn_hist_heights 
            tmn_new_hist_data['bottom'] = np.zeros(len(self._tmn_hist_heights))
            tmn_new_hist_data['left'] = self._hist_bins[:-1]
            tmn_new_hist_data['right'] = self._hist_bins[1:]
            # Push the data to the plot 
            tmn_hist_plot.data_source.data = tmn_new_hist_data
            

        doc.add_periodic_callback(
            callback,
            500
        )
        
        # doc.add_root(
        #     gridplot([[fig, w_fig, tmn_fig]])
        # )
        doc.add_root(column([fig, w_fig, tmn_fig],sizing_mode='stretch_both'))
