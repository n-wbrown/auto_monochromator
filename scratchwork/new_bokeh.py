
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

from auto_monochromator.event_builder import basic_event_builder

from caproto.threading.client import Context

from types import SimpleNamespace


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.debug("imports complete")


class live_1_axis_hist:
    def __init__(self, *args, **kwargs):
        self.data = {'a':deque(maxlen=1000),'b':deque(maxlen=1000)}
        self.make_plot = PeriodicCallback(
            self.make_plot_method,
            500
        )
        self.add_data = PeriodicCallback(
            self.add_data_method,
            10
        )
        self._hist_heights = []
        self._hist_bins = []
        if args.get('data_source') is not None:
            self.outer_data_source=args.get('data_source')
        
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color_map = np.array(grey(11))
        self.to_hist = {
            'left':[],
            'right':[],
            'bottom':[],
            'top':[],
            'fill_alpha':[],
        }

    def make_plot_method(self):
        (
            self._hist_heights, 
            self._hist_bins, 
        ) = np.histogramdd(
            sample=np.array([self.data['a'],self.data['b']]).T,
            bins=np.array([np.arange(-5,5,1),np.arange(-5,10,1)]).T
        )
        self.to_hist = {
            'left':[],
            'right':[],
            'bottom':[],
            'top':[],
            'fill_alpha':[],
        }
        self.lr_bins, self.ud_bins = np.meshgrid(*self._hist_bins)
        self.to_hist['left'] = self.lr_bins[:-1,:-1].flatten()
        self.to_hist['right'] = self.lr_bins[:-1,1:].flatten()
        self.to_hist['bottom'] = self.ud_bins[:-1,:-1].flatten()
        self.to_hist['top'] = self.ud_bins[1:,:-1].flatten()
        alpha = self._hist_heights.flatten('F')/self._hist_heights.max()
        self.to_hist['fill_alpha'] = alpha

    def draw_plot(self, doc):
        fig = figure(y_range=(-6,6),x_range=(-6,6))
        starter_x = np.random.random(5)
        starter_y = np.random.random(5)
        
        hist_plot = fig.quad(
            top=[],
            bottom=[],
            left=[],
            right=[],
            fill_color="green",
            fill_alpha=[],
            line_color="#00FF00"
        )
        circle_plot = fig.circle(
            x=starter_x,
            y=starter_y,
            color="blue",
            size=4
        )
        def callback():

            # create drop-points for new data for plots 
            new_hist_data = dict()
            new_circle_data = dict()
            
            '''
            new_hist_data['fill_color'] = self.color_map[
                self._hist_heights.flatten().astype('int')
            ]
            '''
            new_hist_data['left'] = self.to_hist['left']
            new_hist_data['right'] = self.to_hist['right']
            new_hist_data['bottom'] = self.to_hist['bottom']
            new_hist_data['top'] = self.to_hist['top']
            new_hist_data['fill_alpha'] = self.to_hist['fill_alpha']

           
            # new_circle, push the new dataset 
            new_circle_data['x'] = self.data['a']
            new_circle_data['y'] = self.data['b']
            
            # push new data to plots
            hist_plot.data_source.data = new_hist_data
            circle_plot.data_source.data = new_circle_data
        
        doc.add_periodic_callback(
            callback,
            1000
        )

        doc.add_root(column([fig],sizing_mode='stretch_both'))

    



def aggregator(response, drop_point=None, drop_point_ts=None):
    drop_point.append(response.data)
    drop_point_ts.append(response.metadata.timestamp)
    #print(len(drop_point),flush=True)
    #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",flush=True)
    #print(response.data)
    #print(response.metadata.timestamp)
    #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",flush=True)

def builder(cache, **kwargs):
    series_list = {}
    for x in kwargs:
        sr = pd.Series(kwargs[x]['data'],index=kwargs[x]['time'])
        series_list[x] = sr

    cache.data = basic_event_builder(**series_list)



    
def pv_1axis_hist(live_2_axis_hist):
    def __init__(self, data_source):
        




def launch_server():
    u = live_1_axis_hist()
    v = live_2_axis_hist()

    t = pv_2_axis_hist()



    ca_ctx = Context()
    w, x, y = ca_ctx.get_pvs('beam_sim:w', 'beam_sim:x', 'beam_sim:y')
    n = 100

    w_data = deque(maxlen=n)
    w_time = deque(maxlen=n)
    w_su = w.subscribe(data_type='time')
    w_func = partial(aggregator, drop_point=w_data, drop_point_ts=w_time)
    w_token = w_su.add_callback(w_func)
    
    x_data = deque(maxlen=n)
    x_time = deque(maxlen=n)
    x_su = w.subscribe(data_type='time')
    x_func = partial(aggregator, drop_point=x_data, drop_point_ts=x_time)
    x_token = w_su.add_callback(x_func)
    
    y_data = deque(maxlen=n)
    y_time = deque(maxlen=n)
    y_su = w.subscribe(data_type='time')
    y_func = partial(aggregator, drop_point=y_data, drop_point_ts=y_time)
    y_token = w_su.add_callback(y_func)

    cache = SimpleNamespace()
    
    t = PeriodicCallback(
        partial(
            builder,
            cache=cache,
            **{'w': {'data': w_data,'time': w_time},
            'x': {'data': x_data,'time': x_time},
            'y': {'data': y_data,'time': y_time},
            },
        ),
        500
    )

    e = PeriodicCallback(
        partial(
            print,
            cache,
            "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
            flush=True,
        ),
        500
    )



    
    server = Server(
        {
            '/go':u.draw_plot,
            '/stop':v.draw_plot
            '/new':t.draw_plot,
        },
        num_procs=1
    )
    server.start()
    t.start()
    #e.start()
    #u.make_plot.start()
    #u.add_data.start()
    u.start()
    v.start()
    t.start()
    # Run indefinitely 
    try:
        server.io_loop.start()
    except KeyboardInterrupt:
        print("terminating")
        server.io_loop.stop()


launch_server()
