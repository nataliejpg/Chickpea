import numpy as np

# TODO: write docs
# TODO: read everything once
# TODO: test checks
# TODO: write test
# TODO: check sequence slicing


class Waveform:
    def __init__(self, length=None, channel=None, properties_dict={}):
        if channel:
            self.channel = channel
        else:
            self._channel = None
        if length:
            self._length = int(length)
            self._wave = np.zeros(int(length))
            self._marker_1 = np.zeros(int(length))
            self._marker_2 = np.zeros(int(length))
        else:
            self._length = None
            self._wave = None
            self._marker_1 = None
            self._marker_2 = None

    def clear(self):
        self._wave = np.zeros(self.length)
        self._marker_1 = np.zeros(self.length)
        self._marker_2 = np.zeros(self.length)

    def check(self):
        unset = []
        if self._wave is None:
            unset.append('wave')
        if self._marker_1 is None:
            unset.append('marker1')
        if self._marker_2 is None:
            unset.append('marker2')
        if len(unset) > 0:
            raise Exception(
                'must specify non None array for {}'.format(", ".join(unset)))
        return True

    def _get_channel(self):
        return self._channel

    def _set_channel(self, value):
        if not isinstance(value, int):
            raise TypeError('channel must be integer')
        self._channel = value

    channel = property(_get_channel, _set_channel)

    def _get_length(self):
        return self._length

    def _set_length(self, value):
        if value != self._length:
            self._length = int(value)
            self.clear()

    length = property(_get_length, _set_length)

    def _get_wave(self):
        return self._wave

    def _set_wave(self, wave_array):
        if not self._length:
            self._length = len(wave_array)
        elif self._length != len(wave_array):
            raise Exception('trying to set wave of unexpected length')
        elif not isinstance(wave_array, np.ndarray):
            raise TypeError('wave must be numpy array')
        self._wave = wave_array

    wave = property(_get_wave, _set_wave)

    def _get_marker_1(self):
        return self._marker_1

    def _set_marker_1(self, marker_1_array):
        if not self._length:
            self._length = len(marker_1_array)
        elif self._length != len(marker_1_array):
            raise Exception('trying to set marker_1 of unexpected length')
        elif not isinstance(marker_1_array, np.ndarray):
            raise TypeError('marker_1 must be numpy array')
        self._marker_1 = marker_1_array

    marker_1 = property(_get_marker_1, _set_marker_1)

    def _get_marker_2(self):
        return self._marker_2

    def _set_marker_2(self, marker_2_array):
        if not self._length:
            self._length = len(marker_2_array)
        elif self._length != len(marker_2_array):
            raise Exception('trying to set marker_2 of unexpected length')
        elif not isinstance(marker_2_array, np.ndarray):
            raise TypeError('marker_2 must be numpy array')
        self._marker_2 = marker_2_array

    marker_2 = property(_get_marker_2, _set_marker_2)

    # TODO: decide whether to include below to limit setting waveform
    # attributes

    # def __setattr__(self, name, value):
    # if name not in ('wave', 'marker_1', 'marker_2','length'):
    #     raise AttributeError('attribute %s not allowed' % name)
    # else:
    #     super().__setattr__(name, value)
