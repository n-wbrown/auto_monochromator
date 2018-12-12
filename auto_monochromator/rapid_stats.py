import numpy as np
from collections import deque
from scipy.optimize import curve_fit

class RapidStatsException(Exception):
    pass

class InsufficientDataException(RapidStatsException):
    pass

class DiffDataLenException(RapidStatsException):
    pass

def gaussian(x, mu, sigma, scalar):
    y = np.power(np.e, -1 * ((np.power(x-mu,2))/(2 * np.power(sigma,2))))
    y = 1/np.sqrt(2 * np.pi * np.power(sigma,2)) * y 
    return y * scalar

gvec = np.vectorize(gaussian)

def hist_boxes2d(hist_edges,**kwargs):
    """
    Convert from numpy's histogram edges format to the quad format for bokeh
    plots
    """
    grid_spec = np.meshgrid(*hist_edges)
    box_edges = {}
    box_edges['left'] = grid_spec[0][:-1,:-1].flatten()
    box_edges['right'] = grid_spec[0][:-1,1:].flatten()
    box_edges['bottom'] = grid_spec[1][:-1,:-1].flatten()
    box_edges['top'] = grid_spec[1][1:,:-1].flatten()
    box_edges['lr_center'] = (box_edges['left'] + box_edges['right']) / 2.0
    box_edges['bt_center'] = (box_edges['bottom'] + box_edges['top']) / 2.0
    return box_edges


class BaseHist:
    def push(self):
        raise NotImplementedError

    def hist(self):
        raise NotImplementedError

    @property
    def data(self):
        raise NotImplementedError

    @data.setter
    def data(self):
        raise NotImplementedError


class RapidHist(BaseHist):
    """
    Wrapper on np.histogram for rapidly regenerating histograms of dynamic data
    """
    def __init__(self, maxlen, minlen=None, bins=None, axes=1):
        """
        Parameters
        ----------
        maxlen : int
            Maximum number of data points for hist.

        minlen : int or None
            Minimum number of data points for hist. Causes error to be thrown.

        bins : int, iterable or None
            Set up default bins for the hist following np.histogram rules for
            'bins' argument.
        """
        self.axes = axes
        if self.axes < 1:
            raise Exception("Invalid number of axes")
        self._data = []
        for ax in range(self.axes):
            self._data.append(deque(maxlen=maxlen))
        
        if bins is None:
            self.bins = None
            # self.bins = tuple([10]*self.axes)
        else:
            self.bins = bins
        self.minlen = minlen

    def push(self, data):
        """
        Parameters
        ----------
        data : float, int or iterable
            Append these elements to the data for this hist.
        """
        '''
        if self.axes is 1:
            try:
                self._data.extend(data)
            except TypeError:
                self._data.append(data)
        else:
        '''
        '''
        if self.axes is 1:
            try:
                self._data[0].extend(data)
            except TypeError:
                self._data[0].append(data)
            
        '''
        for data_axis, input_axis in zip(self._data, data):
            try:
                data_axis.extend(input_axis)
            except TypeError:
                data_axis.append(input_axis)

    def hist(self, bins=None, density=False):
        """
        Parameters
        ---------
        bins : int, iterable or None
            Force binning on this hist. Defaults to binning set at class
            instantiation if this is left as None. Argument follows
            np.histogram's rules for 'bins' argument.

        density : bool
            Follows np.histogram's rules for 'density' argument.
        """
        if bins is None:
            bins = self.bins

        for axis in self._data:
            if self.minlen is not None:
                if len(axis) < self.minlen:
                    # raise Exception("Insufficient data")
                    raise InsufficientDataException()
        self.hist_data = np.histogramdd(self._data, bins=bins, density=density)
        return self.hist_data

    def gaussian_fit(self):
        """
        Needs hist to have been recently run.

        Returns
        -------
        (hist_centers, popt, pcov)
        """
        hist_heights, [hist_bins] = self.hist_data
        
        hist_centers = (hist_bins[:-1] + hist_bins[1:]) / 2

        popt, pcov = curve_fit(gaussian, hist_centers, hist_heights)

        return hist_centers, popt, pcov 

    @property
    def data(self):
        return np.array(self._data)


class RapidWeightHist(RapidHist):
    def __init__(self, maxlen, minlen=None, bins=None, axes=1):
        super().__init__(
            maxlen=maxlen,
            minlen=minlen,
            bins=bins,
            axes=axes,
        )
        self._weights = deque(maxlen=maxlen)

    def push(self, data, weights):
        try:
            for axis, w_axis in zip(data,weights):
                if len(axis) is not len(weights):
                    raise DiffDataLenException()
        except TypeError:
            pass
        super().push(data)
        try:
            self._weights.extend(weights)
        except TypeError:
            self._weights.append(weights)

    @property
    def weights(self):
        return np.array(self._weights)

    def hist(self, bins=None, density=False):
        if bins is None:
            bins = self.bins
        for axis in self._data:
            if self.minlen is not None:
                if len(axis) < self.minlen:
                    # raise Exception("Insufficient data")
                    raise InsufficientDataException()
        # print(self._data)
        # print(self._weights)
        self.hist_data = np.histogramdd(
            self._data, 
            weights=self._weights,
            bins=bins, 
            density=density
        )
        return self.hist_data


class RapidTransmissionHist(BaseHist):
    def __init__(self, maxlen, minlen=None, bins=None, axes=1):
        """
        Parameters
        ----------
        maxlen : int
            Maximum number of data points for hist.

        minlen : int or None
            Minimum number of data points for hist. Causes error to be thrown.

        bins : int, iterable or None
            Set up default bins for the hist following np.histogram rules for
            'bins' argument.
        """
        self._data = deque(maxlen=maxlen)
        self.bins = bins
        self.minlen = minlen

        # Abbreviation for incedent energy
        self.inc_hist = RapidHist(
            maxlen=maxlen,
            minlen=minlen,
            bins=bins,
            axes=axes
        )

        self.outgoing_hist = RapidWeightHist(
            maxlen=maxlen,
            minlen=minlen,
            bins=bins,
            axes=axes
        )
    
    def push(self, data, weights):
        """
        Parameters
        ----------
        data : float, int or iterable
            Append these elements to the data for this hist. Must have the same
            length as weights.
        
        weights : float, int or iterable
            Append these elements to the weights for this hist. Must have the
            same length as data.
        """
        self.inc_hist.push(data)
        self.outgoing_hist.push(data,weights)

    @property
    def data(self):
        return self.inc_hist.data

    @property
    def weights(self):
        return self.outgoing_hist.weights

    def hist(self, bins=None, density=False):
        if bins is None:
            bins = self.bins
        for axis in self.inc_hist._data:
            if self.minlen is not None:
                if len(axis) < self.minlen:
                    raise InsufficientDataException()

        inc, bins = self.inc_hist.hist(bins=bins, density=density)
        outgoing, _ = self.outgoing_hist.hist(bins=bins, density=density)
        with np.errstate(divide='ignore',invalid='ignore'):
            fractional_yield = np.nan_to_num(outgoing / inc)
        
        self.hist_data = (fractional_yield, bins)
        return inc, outgoing, fractional_yield, bins
        
    def gaussian_fit(self):
        hist_heights, [hist_bins] = self.hist_data
        hist_centers = (hist_bins[:-1] + hist_bins[1:]) / 2
        popt, pcov = curve_fit(gaussian, hist_centers, hist_heights)

        fractional_yield_gaussian_fit = (hist_centers, popt, pcov)
        return (
            self.inc_hist.gaussian_fit(), 
            self.outgoing_hist.gaussian_fit(),
            fractional_yield_gaussian_fit
        )

        


