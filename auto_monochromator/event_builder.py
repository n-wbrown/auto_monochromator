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
    def __init__(self, *args, **kwargs):
        self.pv_list = kwargs['pv_list']
        self.maxlen = kwargs.get('maxlen',1000)
        self.ctx = Context()
        self.monitors = {}
        self.data_cache = {}
        self.ts_cache = {}
        mon_list = self.ctx.get_pvs(*self.pv_list)
        for pv_name, monitor in zip(self.pv_list, mon_list):
            self.monitors[pv_name] = monitor
            self.data_cache[pv_name] = deque(maxlen=self.maxlen)
            self.ts_cache[pv_name] = deque(maxlen=self.maxlen)

    def subscribe_all(self):
        self.subsc = {}
        for pv_name in self.monitors:
            self.subsc[pv_name] = self.monitors[pv_name].subscribe(
                data_type='time')
        self.cb_tokens = {}
        for pv_name in self.subsc:
            print(pv_name, "************************************")
            f = partial(self.cb_handler)
            def z(*args,**kwargs):
                print("EEE")
            try:
                self.cb_tokens[pv_name] = self.subsc[pv_name].add_callback(
                    self.cb_handler
                    #partial(self.cb_handler,pv_name=pv_name)
                )
            except TimeoutError:
                logger.error("Failed to connect to PV: "+pv_name)
            
    
    def cb_handler(self, *args, **kwargs):
        print("***ARGS",args)
        print("***KWARGS",kwargs)
        #print(pv_name)
        #print(response)
        #self.data_cache[pv_name].append(response.data[0])
        #self.ts_cache[pv_name].append(response.metadata.timestamp)


        
        

