
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
from tornado.ioloop import PeriodicCallback
#import time
import pandas as pd
#import socket
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("imports complete")



class live_1_axis_hist:
    def __init__(self):
        self.data = {'a':deque(maxlen=100),'b':deque(maxlen=100)}
        self.make_plot = PeriodicCallback(
            self.make_plot_method,
            500
        )
        self.add_data = PeriodicCallback(
            self.add_data_method,
            100
        )
        self._hist_heights = []
        self._hist_bins = []
        
    def start(self):
        self.make_plot.start()
        self.add_data.start()

    def add_data_method(self):
        self.data['a'].append(np.random.normal(0,1))
        self.data['b'].append(np.random.normal(2,2))

    def draw_plot(self, doc):
        fig = figure()
        hist_plot = fig.quad(
            top=[],
            bottom=[],
            left=[],
            right=[],
            fill_color="#036564",
            line_color="#033649"
        )

        def callback(count_obj=None):
            #count_obj.i += 1
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


    def make_plot_method(self):
        self._hist_heights, self._hist_bins = np.histogram(self.data['a'])

class live_2_axis_hist(live_1_axis_hist):
    def __init__(self):
        super().__init__()
        self.color_map = np.array(grey(11))

    def make_plot_method(self):
        (
            self._hist_heights, 
            self._hist_bins, 
        ) = np.histogramdd(
            sample=np.array([self.data['a'],self.data['b']]).T,
            bins=np.array([np.arange(-2,2+1,1),np.arange(-4,6+1,1)]).T
        )

    def draw_plot(self, doc):
        fig = figure(y_range=(-6,6),x_range=(-4,6))
        starter_x = np.random.random(5)
        starter_y = np.random.random(5)
        #hist_plot, bins = fig.hexbin(
        #    x=starter_x,
        #    y=starter_y,
        #    size=.3,
        #)
        hist_plot = fig.quad(
            top=[],
            bottom=[],
            left=[],
            right=[],
            fill_color=[],
            line_color="#00FF00"
        )
        circle_plot = fig.circle(
            x=starter_x,
            y=starter_y,
            color="blue",
            size=4
        )
        def callback():
            new_hist_data = dict()
            new_circle_data = dict()
            
            self.lr_bins, self.ud_bins = np.meshgrid(
                self._hist_bins[0], self._hist_bins[1]
            )
            #self.lr_bins = self.lr_bins.flatten('C')
            #self.ud_bins = self.ud_bins.flatten('F')
            
            new_hist_data['left'] = self.lr_bins[:-1,:-1].flatten()
            new_hist_data['right'] = self.lr_bins[:-1,1:].flatten()
            new_hist_data['bottom'] = self.ud_bins[:-1,:-1].flatten()
            new_hist_data['top'] = self.ud_bins[1:,:-1].flatten()
            
            self._hist_heights[self._hist_heights > 10] = 10 
            #self._hist_heights[self._hist_heights > 29] = 29
            
            new_hist_data['fill_color'] = self.color_map[
                self._hist_heights.flatten().astype('int')
            ]
            #new_hist_data['left'] = [0,1]
            #new_hist_data['right'] = [1,2]
            #new_hist_data['bottom'] = [0,2]
            #new_hist_data['top'] = [2,4]
            #new_hist_data['fill_color'] =self.color_map(
            #    self._hist_heights.clip(0,29)
            #)
            new_circle_data['x'] = self.data['a']
            new_circle_data['y'] = self.data['b']
            #print(hist_plot.data_source.data) 
            hist_plot.data_source.data = new_hist_data

            #hist_plot, bins = fig.hexbin(
            #    x=new_hist_data['x'],
            #    y=new_hist_data['y'],
            #    size=.3
            #)
            circle_plot.data_source.data = new_circle_data
        
        doc.add_periodic_callback(
            callback,
            1000
        )

        doc.add_root(column([fig],sizing_mode='stretch_both'))




def launch_server():
    u = live_1_axis_hist()
    v = live_2_axis_hist()


    #t = PeriodicCallback(
    #    partial(
    #        print,
    #        'hello there'
    #    ),
    #    500
    #)

    server = Server(
        {
            '/go':u.draw_plot,
            '/stop':v.draw_plot
        },
        num_procs=1
    )
    server.start()
    #t.start()
    #u.make_plot.start()
    #u.add_data.start()
    u.start()
    v.start()
    # Run indefinitely 
    try:
        server.io_loop.start()
    except KeyboardInterrupt:
        print("terminating")
        server.io_loop.stop()


launch_server()
