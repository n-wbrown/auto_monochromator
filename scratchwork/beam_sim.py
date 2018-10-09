#!/usr/bin/env python3
import random
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import datetime
import numpy as np
import asyncio
import scipy.stats as st





class RandomWalkIOC(PVGroup):
    # delay interval
    dt = pvproperty(value=[.01])
    
    # clock: this one does nothing
    clock = pvproperty(value=[0.0])

    
    
    w = pvproperty(value=[0.0])
    wx_mu = pvproperty(value=[0.0])
    wx_sigma = pvproperty(value=[1.0])
    wx_y = pvproperty(value=[0.0])
    wy_mu = pvproperty(value=[0.0])
    wy_sigma = pvproperty(value=[1.0])
    wy_x = pvproperty(value=[0.0])
    
    x = pvproperty(value=[0.0])
    x_mu = pvproperty(value=[0.0])
    x_sigma = pvproperty(value=[1.0])
    
    y = pvproperty(value=[0.0])
    y_mu = pvproperty(value=[0.0])
    y_sigma = pvproperty(value=[1.0])
    
    
    @clock.startup
    async def clock(self, instance, async_lib):
        'Periodically update the value'
        while True:
            # compute next value
            #print(type(instance))
            #print(type(x))
            #print(self.__dict__)
            # update the ChannelData instance and notify any subscribers
            now = datetime.datetime.now()
            #await instance.write(value=[x],timestamp=now)
            


            x = np.random.normal(self.x_mu.value,self.x_sigma.value)
            y = np.random.normal(self.y_mu.value,self.y_sigma.value)
            await self.attr_pvdb['x'].write(value=[x],timestamp=now)
            await self.attr_pvdb['y'].write(value=[y],timestamp=now)
            


            w = st.multivariate_normal.pdf(
                x=np.array([x,y]),
                mean=np.array([self.wx_mu.value[0],self.wy_mu.value[0]]),
                cov=np.array([
                    [self.wx_sigma.value[0],self.wx_y.value[0]],
                    [self.wy_x.value[0],self.wy_sigma.value[0]]]
                ))
            await self.attr_pvdb['w'].write(value=[w],timestamp=now)

            

            # Let the async library wait for the next iteration
            # await async_lib.library.sleep(self.dt.value[0])
            await asyncio.sleep(self.dt.value[0])

if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='beam_sim:',
        desc='Run an IOC with a random-walking value.')
    print(ioc_options, run_options)
    ioc = RandomWalkIOC(**ioc_options)
    run(ioc.pvdb, **run_options)
