from functools import partial, partialmethod
from collections import deque
import logging

import pandas as pd
import numpy as np
from caproto.threading.client import Context

logger = logging.getLogger(__name__)

def basic_event_builder(*args,**kwargs):
    """
    Pass any number of pandas Series and return an event built pandas
    DataFrame.  Kwargs can be used to name the columns of the returned
    DataFrame.
    """
    data_table = dict()
    [data_table.setdefault(col,args[col]) for col in range(len(args))]
    [data_table.setdefault(col,kwargs[col]) for col in kwargs]
    full_frame = pd.DataFrame(data_table)
    return full_frame.dropna()

class ebuild_mgr:
    """
    This object handles PV subscriptions internally.
    
    The get_data method provides the acumulated data and cleanes internal buffers.
    This object will likely drop points near the time that the get_data method
    is called. This is because data tracking from one get_data block into the next
    will not be succesfully associated with one another and thus dropped.
    """
    def __init__(self, *args, **kwargs):
        self.pv_list = kwargs['pv_list']
        self.maxlen = kwargs.get('maxlen',1000)
        self.ctx = Context()
        self.monitors = {}
        # dict of deque of datapoints from PV
        self.data_cache = {}
        # dict of deque of timestamps from PV - Elementwise match w/ data_cache
        self.ts_cache = {}
        # dict of partial functions - guarentee preservation from gc
        self.cb_cache = {}
        mon_list = self.ctx.get_pvs(*self.pv_list)
        for pv_name, monitor in zip(self.pv_list, mon_list):
            self.monitors[pv_name] = monitor
            self.data_cache[pv_name] = deque(maxlen=self.maxlen)
            self.ts_cache[pv_name] = deque(maxlen=self.maxlen)
            self.cb_cache[pv_name] = partial(self.cb_handler, pv_name=pv_name)

    def subscribe_all(self):
        # Dict of subscription ojbects - to be used for attaching callbacks 
        self.subsc = {}
        for pv_name in self.monitors:
            self.subsc[pv_name] = self.monitors[pv_name].subscribe(
                data_type='time')
        # Dict of callback tokens (from subscriptions created above)
        # Not sure if I need to keep these but I'm doing it just be safe.
        self.cb_tokens = {}
        for pv_name in self.subsc:
            try:
                self.cb_tokens[pv_name] = self.subsc[pv_name].add_callback(
                    self.cb_cache[pv_name]
                )
            except TimeoutError:
                logger.error("Failed to connect to PV: "+pv_name)
            
    
    def cb_handler(self, *args, **kwargs):
        # print("***ARGS",args)
        # print("***KWARGS",kwargs)
        # print(kwargs['pv_name'])
        pv_name = kwargs['pv_name']
        response = args[0]
        # print(response.data[0])
        # print(response.metadata.timestamp)
        self.data_cache[pv_name].append(response.data[0])
        self.ts_cache[pv_name].append(response.metadata.timestamp)
        print("success")
        #print(pv_name)
        #print(response)
        #self.data_cache[pv_name].append(response.data[0])
        #self.ts_cache[pv_name].append(response.metadata.timestamp)

    def get_data(self):
        data_series = {}
        for pv_name in self.subsc:
            data_series[pv_name] = pd.Series(
                list(self.data_cache[pv_name]),
                index=list(self.ts_cache[pv_name]))
        
        return basic_event_builder(**data_series)



        
        

