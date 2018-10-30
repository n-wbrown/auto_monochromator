import logging 
import pandas as pd
import numpy as np
import pytest
import h5py
import os
logger = logging.getLogger(__name__)

@pytest.fixture(scope='module')
def sxrR6_dataFrame():
    directory = os.path.dirname(os.path.realpath(__file__))
    test_file_path = os.path.join(directory, "sxrx30116run6_slim.h5") 
    file = h5py.File(test_file_path)
    return file


@pytest.fixture(scope='function')
def histogram_edges():
    data = [
        np.array([
            -0.57581821,  0.56039377,  1.69660575,  2.83281772,  3.9690297,
            5.10524168,  6.24145365,  7.37766563,  8.51387761,  9.65008958,
            10.78630156]), 
        np.array([
            -2.44160903, -1.68404432, -0.9264796 , -0.16891488,  0.58864984,
            1.34621456,  2.10377928,  2.861344  ,  3.61890872,  4.37647343,
            5.13403815])]
    return data

@pytest.fixture(scope='function')
def histogram_rect_bins():
    data = {}
    data['left'] = np.array([
        -0.57581821,  0.56039377,  1.69660575,  2.83281772,  3.9690297 ,
         5.10524168,  6.24145365,  7.37766563,  8.51387761,  9.65008958,
        -0.57581821,  0.56039377,  1.69660575,  2.83281772,  3.9690297 ,
         5.10524168,  6.24145365,  7.37766563,  8.51387761,  9.65008958,
        -0.57581821,  0.56039377,  1.69660575,  2.83281772,  3.9690297 ,
         5.10524168,  6.24145365,  7.37766563,  8.51387761,  9.65008958,
        -0.57581821,  0.56039377,  1.69660575,  2.83281772,  3.9690297 ,
         5.10524168,  6.24145365,  7.37766563,  8.51387761,  9.65008958,
        -0.57581821,  0.56039377,  1.69660575,  2.83281772,  3.9690297 ,
         5.10524168,  6.24145365,  7.37766563,  8.51387761,  9.65008958,
        -0.57581821,  0.56039377,  1.69660575,  2.83281772,  3.9690297 ,
         5.10524168,  6.24145365,  7.37766563,  8.51387761,  9.65008958,
        -0.57581821,  0.56039377,  1.69660575,  2.83281772,  3.9690297 ,
         5.10524168,  6.24145365,  7.37766563,  8.51387761,  9.65008958,
        -0.57581821,  0.56039377,  1.69660575,  2.83281772,  3.9690297 ,
         5.10524168,  6.24145365,  7.37766563,  8.51387761,  9.65008958,
        -0.57581821,  0.56039377,  1.69660575,  2.83281772,  3.9690297 ,
         5.10524168,  6.24145365,  7.37766563,  8.51387761,  9.65008958,
        -0.57581821,  0.56039377,  1.69660575,  2.83281772,  3.9690297 ,
         5.10524168,  6.24145365,  7.37766563,  8.51387761,  9.65008958])
    data['right'] = np.array([
        0.56039377,  1.69660575,  2.83281772,  3.9690297 ,  5.10524168,
        6.24145365,  7.37766563,  8.51387761,  9.65008958, 10.78630156,
        0.56039377,  1.69660575,  2.83281772,  3.9690297 ,  5.10524168,
        6.24145365,  7.37766563,  8.51387761,  9.65008958, 10.78630156,
        0.56039377,  1.69660575,  2.83281772,  3.9690297 ,  5.10524168,
        6.24145365,  7.37766563,  8.51387761,  9.65008958, 10.78630156,
        0.56039377,  1.69660575,  2.83281772,  3.9690297 ,  5.10524168,
        6.24145365,  7.37766563,  8.51387761,  9.65008958, 10.78630156,
        0.56039377,  1.69660575,  2.83281772,  3.9690297 ,  5.10524168,
        6.24145365,  7.37766563,  8.51387761,  9.65008958, 10.78630156,
        0.56039377,  1.69660575,  2.83281772,  3.9690297 ,  5.10524168,
        6.24145365,  7.37766563,  8.51387761,  9.65008958, 10.78630156,
        0.56039377,  1.69660575,  2.83281772,  3.9690297 ,  5.10524168,
        6.24145365,  7.37766563,  8.51387761,  9.65008958, 10.78630156,
        0.56039377,  1.69660575,  2.83281772,  3.9690297 ,  5.10524168,
        6.24145365,  7.37766563,  8.51387761,  9.65008958, 10.78630156,
        0.56039377,  1.69660575,  2.83281772,  3.9690297 ,  5.10524168,
        6.24145365,  7.37766563,  8.51387761,  9.65008958, 10.78630156,
        0.56039377,  1.69660575,  2.83281772,  3.9690297 ,  5.10524168,
        6.24145365,  7.37766563,  8.51387761,  9.65008958, 10.78630156]) 
    data['bottom'] = np.array([
        -2.44160903, -2.44160903, -2.44160903, -2.44160903, -2.44160903,
        -2.44160903, -2.44160903, -2.44160903, -2.44160903, -2.44160903,
        -1.68404432, -1.68404432, -1.68404432, -1.68404432, -1.68404432,
        -1.68404432, -1.68404432, -1.68404432, -1.68404432, -1.68404432,
        -0.9264796 , -0.9264796 , -0.9264796 , -0.9264796 , -0.9264796 ,
        -0.9264796 , -0.9264796 , -0.9264796 , -0.9264796 , -0.9264796 ,
        -0.16891488, -0.16891488, -0.16891488, -0.16891488, -0.16891488,
        -0.16891488, -0.16891488, -0.16891488, -0.16891488, -0.16891488,
         0.58864984,  0.58864984,  0.58864984,  0.58864984,  0.58864984,
         0.58864984,  0.58864984,  0.58864984,  0.58864984,  0.58864984,
         1.34621456,  1.34621456,  1.34621456,  1.34621456,  1.34621456,
         1.34621456,  1.34621456,  1.34621456,  1.34621456,  1.34621456,
         2.10377928,  2.10377928,  2.10377928,  2.10377928,  2.10377928,
         2.10377928,  2.10377928,  2.10377928,  2.10377928,  2.10377928,
         2.861344  ,  2.861344  ,  2.861344  ,  2.861344  ,  2.861344  ,
         2.861344  ,  2.861344  ,  2.861344  ,  2.861344  ,  2.861344  ,
         3.61890872,  3.61890872,  3.61890872,  3.61890872,  3.61890872,
         3.61890872,  3.61890872,  3.61890872,  3.61890872,  3.61890872,
         4.37647343,  4.37647343,  4.37647343,  4.37647343,  4.37647343,
         4.37647343,  4.37647343,  4.37647343,  4.37647343,  4.37647343])
    data['top'] = np.array([
        -1.68404432, -1.68404432, -1.68404432, -1.68404432, -1.68404432,
        -1.68404432, -1.68404432, -1.68404432, -1.68404432, -1.68404432,
        -0.9264796 , -0.9264796 , -0.9264796 , -0.9264796 , -0.9264796 ,
        -0.9264796 , -0.9264796 , -0.9264796 , -0.9264796 , -0.9264796 ,
        -0.16891488, -0.16891488, -0.16891488, -0.16891488, -0.16891488,
        -0.16891488, -0.16891488, -0.16891488, -0.16891488, -0.16891488,
         0.58864984,  0.58864984,  0.58864984,  0.58864984,  0.58864984,
         0.58864984,  0.58864984,  0.58864984,  0.58864984,  0.58864984,
         1.34621456,  1.34621456,  1.34621456,  1.34621456,  1.34621456,
         1.34621456,  1.34621456,  1.34621456,  1.34621456,  1.34621456,
         2.10377928,  2.10377928,  2.10377928,  2.10377928,  2.10377928,
         2.10377928,  2.10377928,  2.10377928,  2.10377928,  2.10377928,
         2.861344  ,  2.861344  ,  2.861344  ,  2.861344  ,  2.861344  ,
         2.861344  ,  2.861344  ,  2.861344  ,  2.861344  ,  2.861344  ,
         3.61890872,  3.61890872,  3.61890872,  3.61890872,  3.61890872,
         3.61890872,  3.61890872,  3.61890872,  3.61890872,  3.61890872,
         4.37647343,  4.37647343,  4.37647343,  4.37647343,  4.37647343,
         4.37647343,  4.37647343,  4.37647343,  4.37647343,  4.37647343,
         5.13403815,  5.13403815,  5.13403815,  5.13403815,  5.13403815,
         5.13403815,  5.13403815,  5.13403815,  5.13403815,  5.13403815])

    return data
