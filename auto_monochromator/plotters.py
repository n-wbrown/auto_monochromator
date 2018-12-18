from functools import partial
from collections import deque

import numpy as np
from bokeh.plotting import figure
from bokeh.layouts import column, row, gridplot
from bokeh.server.server import Server
from bokeh.layouts import widgetbox
from bokeh.models.widgets import PreText, Div
from bokeh.models import Spacer
from bokeh.palettes import RdYlBu3, grey
from tornado.ioloop import PeriodicCallback, IOLoop
import pandas as pd
import logging

from caproto.threading.client import Context

from .event_builder import ebuild_mgr
from .rapid_stats import (RapidHist, RapidWeightHist, 
    RapidTransmissionHist, InsufficientDataException, gaussian,
    RapidWeightTransmissionHist)


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
        self.inherited = kwargs.get('inherited',False)

        self.data = RapidTransmissionHist(maxlen=self.maxlen)
        self.pv = kwargs['pv']
        self.weight = kwargs['weight']

        if not self.inherited:
            self.ebuild = ebuild_mgr(pv_list=[self.pv, self.weight],maxlen=self.maxlen)
            self.ebuild.subscribe_all()
        
        self.hist_fit = ([], [], [])
        self.w_hist_fit = ([], [], [])
        self.tmn_hist_fit = ([], [], [])

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
        super().__init__(*args,**kwargs)
        # Use "poly" or "gaussian"
        self.fit_type = kwargs.get('fit_type', 'gaussian')
        self._hist_heights = []
        self._hist_bins = []
        self._w_hist_heights = []
        self._tmn_hist_heights = []
        self.fig_title = "Incident Hits"
        self.w_fig_title = "Weighted Exit Hits"
        self.tmn_fig_title = "Transmission"

    def make_plot_method(self):
        try:
            self._hist_heights, self._w_hist_heights, self._tmn_hist_heights, [self._hist_bins] = self.data.hist(bins=20)
            if self.fit_type is "gaussian":
                self.hist_fit, self.w_hist_fit, self.tmn_hist_fit = self.data.gaussian_fit()
            elif self.fit_type is "poly":
                self.hist_fit, self.w_hist_fit, self.tmn_hist_fit = self.data.poly_fit()
            
            # print("*************************")
            # print(self.hist_fit)
            # print(self.w_hist_fit)
            # print(self.tmn_hist_fit)

            # print("[    mu,     sigma,      scalar]")
            # print("raw:         ",self.hist_fit[1])
            # print("weighted:    ",self.w_hist_fit[1])
            # print("transmission:",self.tmn_hist_fit[1])
            # print("error:       ",self.tmn_hist_fit[1][0]-self.hist_fit[1][0])
            if self.fit_type is "gaussian":
                self._hist_fit = gaussian( self.hist_fit[0], *self.hist_fit[1])
                self._w_hist_fit = gaussian( self.w_hist_fit[0], *self.w_hist_fit[1])
                self._tmn_hist_fit = gaussian( self.tmn_hist_fit[0], *self.tmn_hist_fit[1])
            elif self.fit_type is "poly": 
                self._hist_fit = np.polyval( self.hist_fit[1], self.hist_fit[0])
                self._w_hist_fit = np.polyval( self.w_hist_fit[1], self.w_hist_fit[0])
                self._tmn_hist_fit = np.polyval( self.tmn_hist_fit[1], self.tmn_hist_fit[0])
                self.center =  -1 * self.hist_fit[1][1] / (2 * self.hist_fit[1][0])
                self.w_center =  -1 * self.w_hist_fit[1][1] / (2 * self.w_hist_fit[1][0])
                self.tmn_center = -1 * self.tmn_hist_fit[1][1] / (2 * self.tmn_hist_fit[1][0])

        except InsufficientDataException:
            print("insufficientDataException")
        except RuntimeError:
            print("RUNTIME ERROR")

    def draw_plot(self, doc):
        # Create figure and figure-like entities
        fig = figure(title=self.fig_title)
        stats_text = PreText(text="loading...")
        w_fig = figure(title=self.w_fig_title,x_range=fig.x_range)
        w_stats_text = PreText(text="loading...")
        tmn_fig = figure(title=self.tmn_fig_title,x_range=fig.x_range)
        tmn_stats_text = PreText(text="loading...")
        
        # Add plots to the figures 
        hist_plot = fig.quad(
            top=[0],
            bottom=[1],
            left=[0],
            right=[1],
            fill_color="#036564",
            line_color="#033649"
        )
        hist_fit_line = fig.line(
            x = [0],
            y = [0],
            line_width = 5,
        )
        w_hist_plot = w_fig.quad(
            top=[0],
            bottom=[1],
            left=[0],
            right=[1],
            fill_color="#036564",
            line_color="#033649"
        )
        w_hist_fit_line = w_fig.line(
            x = [0],
            y = [0],
            line_width = 5,
        )
        tmn_hist_plot = tmn_fig.quad(
            top=[0],
            bottom=[1],
            left=[0],
            right=[1],
            fill_color="#036564",
            line_color="#033649"
        )
        tmn_hist_fit_line = tmn_fig.line(
            x = [0],
            y = [0],
            line_width = 5,
        )

        def callback():
            new_hist_data = dict()
            new_hist_data['top'] =  self._hist_heights 
            new_hist_data['bottom'] = np.zeros(len(self._hist_heights))
            new_hist_data['left'] = self._hist_bins[:-1]
            new_hist_data['right'] = self._hist_bins[1:]
            # Push the data to the plot 
            hist_plot.data_source.data = new_hist_data

            new_hist_fit_data = dict()
            new_hist_fit_data['x'] = self.hist_fit[0]
            new_hist_fit_data['y'] = self._hist_fit
            hist_fit_line.data_source.data = new_hist_fit_data
            if self.fit_type is "gaussian":
                stats_str = (
                    "mu:     {:15.5f}\n" + 
                    "sigma:  {:15.5f}\n" + 
                    "scalar: {:15.5f}\n"
                )
            elif self.fit_type is "poly": 
                stats_str = (
                    "a:      {:15.5f}\n" + 
                    "b:      {:15.5f}\n" + 
                    "c:      {:15.5f}\n" +
                    "center: {:15.5f}\n"
                )
            if self.fit_type is "gaussian":
                stats_text.text = stats_str.format(*self.hist_fit[1])
            elif self.fit_type is "poly":
                stats_text.text = stats_str.format(
                    *self.hist_fit[1],
                    self.center
                )
            
            w_new_hist_data = dict()
            w_new_hist_data['top'] =  self._w_hist_heights 
            w_new_hist_data['bottom'] = np.zeros(len(self._w_hist_heights))
            w_new_hist_data['left'] = self._hist_bins[:-1]
            w_new_hist_data['right'] = self._hist_bins[1:]
            # Push the data to the plot 
            w_hist_plot.data_source.data = w_new_hist_data

            w_new_hist_fit_data = dict()
            w_new_hist_fit_data['x'] = self.w_hist_fit[0]
            w_new_hist_fit_data['y'] = self._w_hist_fit
            w_hist_fit_line.data_source.data = w_new_hist_fit_data
            
            if self.fit_type is "gaussian":
                w_stats_str = (
                    "mu:     {:15.5f}\n" + 
                    "sigma:  {:15.5f}\n" + 
                    "scalar: {:15.5f}\n"
                )
            elif self.fit_type is "poly":
                w_stats_str = (
                    "a:      {:15.5f}\n" + 
                    "b:      {:15.5f}\n" + 
                    "c:      {:15.5f}\n" +
                    "center: {:15.5f}\n"
                )                

            if self.fit_type is "gaussian":
                w_stats_text.text = w_stats_str.format(*self.w_hist_fit[1])
            elif self.fit_type is "poly":
                w_stats_text.text = w_stats_str.format(
                    *self.w_hist_fit[1],
                    self.w_center
                )

            tmn_new_hist_data = dict()
            tmn_new_hist_data['top'] =  self._tmn_hist_heights 
            tmn_new_hist_data['bottom'] = np.zeros(len(self._tmn_hist_heights))
            tmn_new_hist_data['left'] = self._hist_bins[:-1]
            tmn_new_hist_data['right'] = self._hist_bins[1:]
            # Push the data to the plot 
            tmn_hist_plot.data_source.data = tmn_new_hist_data

            tmn_new_hist_fit_data = dict()
            tmn_new_hist_fit_data['x'] = self.tmn_hist_fit[0]
            tmn_new_hist_fit_data['y'] = self._tmn_hist_fit
            tmn_hist_fit_line.data_source.data = tmn_new_hist_fit_data

            if self.fit_type is "gaussian":
                tmn_stats_str = (
                    "mu:     {:15.5f}\n" + 
                    "sigma:  {:15.5f}\n" + 
                    "scalar: {:15.5f}\n\n" +
                    "error: {:15.5f}\n" + 
                    "(error = Transmission_mu - Incident_mu)"
                )
            elif self.fit_type is "poly":
                tmn_stats_str = (
                    "a:      {:15.5f}\n" + 
                    "b:      {:15.5f}\n" + 
                    "c:      {:15.5f}\n" +
                    "center: {:15.5f}\n" +
                    "error:  {:15.5f}\n" +
                    "(error = Transmission_center - Incident_center)"
                )

            if self.fit_type is "gaussian":
                tmn_stats_text.text = tmn_stats_str.format(
                    *self.tmn_hist_fit[1],
                    self.tmn_hist_fit[1][0]-self.hist_fit[1][0],
                )
            elif self.fit_type is "poly":
                
                tmn_stats_text.text = tmn_stats_str.format(
                    *self.tmn_hist_fit[1],
                    self.tmn_center,
                    self.tmn_center - self.center,
                )

        doc.add_periodic_callback(
            callback,
            500
        )
        
        doc.add_root(row(
            column(
                fig, w_fig, tmn_fig,
                sizing_mode='stretch_both'
            ),
            column(
                widgetbox(stats_text),
                widgetbox(w_stats_text),
                widgetbox(tmn_stats_text),
                # Spacer(width=20,height=1),
                sizing_mode='stretch_both'
            ), 
            sizing_mode='stretch_both'
        ))


class triple_w_histogram_1d(triple_histogram_1d):
    def __init__(self,*args,**kwargs):
        kwargs['inherited'] = True 
        super().__init__(*args,**kwargs)
        # Use "poly" or "gaussian"

        self.data = RapidWeightTransmissionHist(maxlen=self.maxlen)
        self.in_weight = kwargs['in_weight']
        self.ebuild = ebuild_mgr(
            pv_list=[self.pv, self.weight, self.in_weight],
            maxlen=self.maxlen)
        self.ebuild.subscribe_all()

        self.fig_title = "Weighted Incident Hits"
        self.w_fig_title = "Weighted Exit Hits"
        self.tmn_fig_title = "Transmission"

    def add_data_method(self):
        data_package = self.ebuild.get_data()
        self.data.push(
            data = [data_package[self.pv].values],
            weights_out = data_package[self.weight].values,
            weights_in = data_package[self.in_weight].values
        )

