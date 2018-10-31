import versioneer
from setuptools import setup, find_packages

setup(
    name='auto_monochromator',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    license='BSD',
    author='SLAC National Accelerator Laboratories',
    packages=find_packages(),
    description='Toolset for automated mochromator tuning',
    scripts=['bin/bokeh_monitor'],
    entry_points = {
        'console_scripts': ['beam_sim = auto_monochromator.beam_sim:main'] 
    })
