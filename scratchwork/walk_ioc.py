#!/usr/bin/env python3
import random
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import datetime


class RandomWalkIOC(PVGroup):
    dt = pvproperty(value=[3.0])
    x = pvproperty(value=[0.0])
    y = pvproperty(value=[0.0])

    @x.startup
    async def x(self, instance, async_lib):
        'Periodically update the value'
        while True:
            # compute next value
            x, = self.x.value
            x += random.random()
            #print(type(instance))
            #print(type(x))
            #print(self.__dict__)
            # update the ChannelData instance and notify any subscribers
            td = datetime.timedelta(hours=27)
            now = datetime.datetime.now()
            await instance.write(value=[x],timestamp=now-td)

            await self.attr_pvdb['y'].write(value=[x+3],timestamp=now+td)

            # Let the async library wait for the next iteration
            await async_lib.library.sleep(self.dt.value[0])


if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='random_walk:',
        desc='Run an IOC with a random-walking value.')
    print(ioc_options, run_options)
    ioc = RandomWalkIOC(**ioc_options)
    run(ioc.pvdb, **run_options)
