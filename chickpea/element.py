import copy
import logging
from typing import List
import warnings

try:
    import matplotlib.pyplot as plt
except RuntimeError as e:
    warnings.warn('Could not import matplotlib {}'.format(e))

from . import Waveform

log = logging.getLogger(__name__)


class Element:
    """
    Element class which represents the element of a sequence
    and is a dictionary of the waveforms running on channels of
    the AWG at one point in time.
    ie one element has many waveforms (one per channel)
       one sequence has many elements
    """

    def __init__(self, sample_rate: float = None):
        """
        Args:
            sample_rate attribute
        """
        self._waveforms = {}
        self.sample_rate = sample_rate

    def __getitem__(self, key):
        return self._waveforms[key]

    def __setitem__(self, key: int, value: Waveform):
        self._waveforms[key] = value

    def __repr__(self):
        return repr(self._waveforms)

    def __len__(self):
        return len(self._waveforms)

    def __delitem__(self, key):
        del self._waveforms[key]

    def _set_sample_rate(self, val: float):
        if self._waveforms:
            for w in self._waveforms.values():
                w.sample_rate = val
        self._sample_rate = val

    def _get_sample_rate(self):
        return self._sample_rate

    sample_rate = property(fget=_get_sample_rate, fset=_set_sample_rate)

    def _get_duration(self):
        if self._sample_rate is None:
            raise RuntimeError('Cannot get duration as sample_rate is None')
        else:
            return next(iter(self._waveforms.values())).duration

    duration = property(fget=_get_duration)

    def clear(self):
        self._waveforms.clear()

    def add_waveform(self, waveform: Waveform, channel: int = None):
        if self.sample_rate is not None:
            if waveform.sample_rate is None:
                waveform.sample_rate = self.sample_rate
            elif waveform.sample_rate != self.sample_rate:
                raise ValueError('Cannot add a waveform with a different'
                                 'sample rate to that of the element. '
                                 'element SR: {}, waveform SR: {}'.format(
                                     self.sample_rate, waveform.sample_rate))
        if channel is not None:
            if ((waveform.channel is not None) and
                    (channel != waveform.channel)):
                raise ValueError('Trying to add Waveform with channel {} to '
                                 'channel {} of element'.format(
                                     waveform.channel, channel))
            waveform.channel = channel
        self[waveform.channel] = waveform

    def plot(self, channels: List[int]=None):
        """
        Plots the waves and markers from selected channels
        in a matplotlib.pyplot subplot

        Args:
            subplot to plot on, otherwise makes a new figure

        Returns:
            plot
        """
        if channels is None:
            channels = list(self.keys())
        try:
            fig = plt.figure()
        except NameError as e:
            raise Warning('Could not create matplot figure {}'.format(e))
        plt_count = len(channels)
        for i, chan in enumerate(channels):
            index = (plt_count * 100) + 10 + i + 1
            ax = fig.add_subplot(index)
            self[chan].plot(subplot=ax)
        plt.tight_layout()
        return fig

    def print_segment_lists(self, channels: List[int]=None):
        """
        Prints a formatted segment list for each channel of the element
        """
        if channels is None:
            channels = list(self.keys())
        if any(sl is None for sl in [self[c].segment_list for c in channels]):
            print('not all channels are made of segment lists')
        else:
            seg_len = len(self[channels[0]].segment_list)
            if not all(len(self[c].segment_list) == seg_len for c in channels):
                for c in channels:
                    print('ch {}: {}'.format(c, self[c].segment_list))
            else:
                template = ''
                for s in range(seg_len):
                    str_length = max(len(self[c].segment_list[s].name)
                                     for c in channels)
                    template += '{: <' + str(str_length) + '}|'
                for c in channels:
                    print('ch ', c, ': ', template[:-1].format(
                        *self[c].segment_list))

    def check(self):
        """
        Function which checks:
        1) element dictionary is not empty,
        2) runs check on all waveforms
        3) that the lengths of the waveforms are all the same.
        """
        if not self._waveforms:
            raise RuntimeError('no waveforms in element')
        if any(type(k) is not int for k in self._waveforms.keys()):
            raise RuntimeError('Found non int waveform channel in element '
                               'dict. Keys: {}'.format(self._waveforms.keys()))
        for i, waveform in enumerate(self._waveforms.values()):
            try:
                waveform.check()
            except RuntimeError as e:
                raise RuntimeError(
                    'error in waveform {}: {}'.format(i, e))
        lengths = [len(w) for w in self._waveforms.values()]
        if lengths.count(lengths[0]) != len(lengths):
            raise RuntimeError(
                'the waveforms of this element are '
                'not of equal length: {}'.format(str(lengths)))

        return True

    def copy(self):
        return copy.deepcopy(self)

    def has_key(self, k):
        return k in self._waveforms

    def update(self, *args, **kwargs):
        return self._waveforms.update(*args, **kwargs)

    def keys(self):
        return self._waveforms.keys()

    def values(self):
        return self._waveforms.values()

    def items(self):
        return self._waveforms.items()

    def pop(self, *args):
        return self._waveforms.pop(*args)

    def __cmp__(self, dict):
        return cmp(self._waveforms, dict)

    def __contains__(self, item):
        return item in self._waveforms

    def __iter__(self):
        return iter(self._waveforms)
