#!/usr/bin/env python3
import random
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import datetime
import numpy as np
import asyncio
import scipy.stats as st
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RandomWalkIOC(PVGroup):
    # delay interval
    dt = pvproperty(value=[.02])
    
    # clock: this one does nothing
    clock = pvproperty(value=[0.0])

    w = pvproperty(value=[0.0])
    wx_mu = pvproperty(value=[0.0])
    wx_sigma = pvproperty(value=[1.0])
    wx_y = pvproperty(value=[0.0])
    wy_mu = pvproperty(value=[0.0])
    wy_sigma = pvproperty(value=[1.0])
    wy_x = pvproperty(value=[0.0])
    w_noise = pvproperty(value=[0.0])

    v = pvproperty(value=[0.0])
    vx_mu = pvproperty(value=[0.0])
    vx_sigma = pvproperty(value=[1.0])
    vx_y = pvproperty(value=[0.0])
    vy_mu = pvproperty(value=[0.0])
    vy_sigma = pvproperty(value=[1.0])
    vy_x = pvproperty(value=[0.0])
    v_noise = pvproperty(value=[0.0])



    
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
                mean=np.array([self.wx_mu.value,self.wy_mu.value]),
                cov=np.array([
                    [self.wx_sigma.value,self.wx_y.value],
                    [self.wy_x.value,self.wy_sigma.value]]
                ))
            w *= (1 + np.random.normal(scale=self.w_noise.value))
            await self.attr_pvdb['w'].write(value=[w],timestamp=now)
            
            v = st.multivariate_normal.pdf(
                x=np.array([x,y]),
                mean=np.array([self.vx_mu.value,self.vy_mu.value]),
                cov=np.array([
                    [self.vx_sigma.value,self.vx_y.value],
                    [self.vy_x.value,self.vy_sigma.value]]
                ))
            v *= (1 + np.random.normal(scale=self.v_noise.value))
            await self.attr_pvdb['w'].write(value=[v],timestamp=now)         
            
            # Let the async library wait for the next iteration
            # await async_lib.library.sleep(self.dt.value[0])
            await asyncio.sleep(self.dt.value)

if __name__ == '__main__':
    main()

def main():
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='beam_sim:',
        desc='Run an IOC with a random-walking value.')
    print(ioc_options, run_options)
    ioc = RandomWalkIOC(**ioc_options)
    for itm in ioc.attr_pvdb:
        logging.info(" pv: \t" + str(ioc.prefix) + str(itm))
    run(ioc.pvdb, **run_options)
