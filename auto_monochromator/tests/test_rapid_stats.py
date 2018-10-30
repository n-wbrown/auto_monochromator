import logging 
import pandas as pd
import numpy as np
from auto_monochromator.rapid_stats import (RapidHist, RapidWeightHist,
    RapidTransmissionHist, hist_boxes2d)
from collections import deque
logger = logging.getLogger(__name__)


def test_hist_boxes2d(histogram_edges, histogram_rect_bins):
    given_hist_edges = histogram_edges
    result_edges = hist_boxes2d(given_hist_edges)
    for edge in ["left","right","bottom","top"]:
        assert np.all(result_edges[edge] == histogram_rect_bins[edge])


def test_RapidHist_push():
    rh = RapidHist(
        maxlen = 5,
        minlen = 3,
        bins = [list(range(5))]
    )
    data = list(range(3))*10
    rh.push([data])
    print(rh.data)
    assert np.all(rh.data == np.array([[1,2,0,1,2]]))


def test_RapidHist_hist():
    rh = RapidHist(
        maxlen = 5,
        minlen = 3,
        bins = [list(range(5))]
    )
    data = list(range(3))*10
    rh.push([data])
    hits, bins = rh.hist()
    logger.debug(hits,bins)
    assert np.all(hits == np.array([1,2,2,0]))
    assert np.all(bins == np.array(list(range(5))))


def test_nd_RapidHist_hist():
    rh = RapidHist(
        maxlen = 5,
        minlen = 1,
        bins = [list(range(4)),list(range(4))],
        axes=2
    )
    data = [[0,0,2,2,2],[0,2,2,2,2]]
    rh.push(data)
    hits, bins = rh.hist()
    print(hits,bins)
    target = np.array(
        [
            [1,0,1],
            [0,0,0],
            [0,0,3],
        ]
    )
    assert np.all(hits == target)


def test_RapidWeightHist_push():
    rwh = RapidWeightHist(
        maxlen = 5,
        minlen = 3,
        bins = [list(range(5))]
    )
    data = list(range(3))*10
    weights = np.array(list(range(3))*10)
    rwh.push([data], weights)
    assert np.all(rwh.data == np.array([1,2,0,1,2]))
    assert np.all(rwh.weights == np.array([1,2,0,1,2]))


def test_RapidWeightHist_hist():
    rwh = RapidWeightHist(
        maxlen = 5,
        minlen = 3,
        bins = [list(range(5))]
    )
    data = list(range(3))*10
    weights = list(range(3))*10
    rwh.push([data], weights)
    hits, bins = rwh.hist()
    print(hits,bins)
    assert np.all(hits == np.array([0,2,4,0]))
    assert np.all(bins == np.array(list(range(5))))
    

def test_RapidTransmissionHist_push():
    rth = RapidTransmissionHist(
        maxlen=5,
        minlen=3,
        bins = [list(range(5))]
    )
    data = np.array([1,1,1,2,3]), # bin that the hit falls into
    weights = np.array([12,8,1,4,5]), # power per hit
     
    rth.push(
        [data], # bin that the hit falls into
        weights, # power per hit
    )

    assert np.all(data == rth.data)
    assert np.all(weights == rth.weights)


def test_RapidTransmissionHist_hist():
    rth = RapidTransmissionHist(
        maxlen = 5,
        minlen = 3,
        bins = [list(range(5))]
    )
    data = np.array([1,1,1,2,3]) # bin that the hit falls into
    weights = np.array([3,8,1,2,4]) # power per hit
    rth.push([data],weights)
    inc, outgoing, hist, bins = rth.hist()
    
    #assert np.all(hist == np.array([0, 11, 5, 2]))
    print(type(hist))
    assert np.all(hist == np.array([0, 4, 2, 4]))
