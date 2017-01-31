import numpy as np

# TODO: test checks
# TODO: write tests
# TODO: check sequence slicing behaviour


class Waveform:
    def __init__(self, length=None, channel=None):
        """
        Waveform class which represents the wave and markers
        (as numpy arrays) for one channel
        of the AWG at one point in time.
        ie one element has many elements (one per channel)

        Args:
            length (int): optional number of points
            channel (int): optional channel to assign to when in an element
        """

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
        """
        Function which sets the wave and markers of the waveform to zeros
        """
        self._wave = np.zeros(self.length)
        self._marker_1 = np.zeros(self.length)
        self._marker_2 = np.zeros(self.length)

    def check(self):
        """
        Function which checks that the wave and markers are all set

        nb doesn't check that they are all the same length because
        it should b impossible to make them otherwise
        """
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
        """
        Get or set the channel of the waveform
        - channel (int)
        """
        return self._channel

    def _set_channel(self, value):
        if not isinstance(value, int):
            raise AttributeError('channel must be integer')
        self._channel = value

    channel = property(_get_channel, _set_channel)

    def _get_length(self):
        """
        Get or set the length of the wave and markers
        if set is called and is different than current value
        it sets all elements to 0
        - length (int)
        """
        return self._length

    def _set_length(self, value):
        if value != self._length:
            self._length = int(value)
            self.clear()

    length = property(_get_length, _set_length)

    def _get_wave(self):
        """
        Get or set the wave of the waveform
        -  wave (numpy array)
        """
        return self._wave

    def _set_wave(self, wave_array):
        if not self._length:
            self._length = len(wave_array)
        elif self._length != len(wave_array):
            raise AttributeError('trying to set wave of unexpected length')
        elif not isinstance(wave_array, np.ndarray):
            raise AttributeError('wave must be numpy array')
        elif max(abs(wave_array)) > 1:
            raise AttributeError('wave values outside (-1, 1)')
        self._wave = wave_array

    wave = property(_get_wave, _set_wave)

    def _get_marker_1(self):
        """
        Get or set the marker_1 of the waveform
        -  marker_1 (numpy array)
        """
        return self._marker_1

    def _set_marker_1(self, marker_1_array):
        if not self._length:
            self._length = len(marker_1_array)
        elif self._length != len(marker_1_array):
            raise AttributeError('trying to set marker_1 of unexpected length')
        elif not isinstance(marker_1_array, np.ndarray):
            raise AttributeError('marker_1 must be numpy array')
        elif any(int(m) not in [0, 1] for m in marker_1_array):
            raise AttributeError('marker_1 values not in (0, 1)')
        self._marker_1 = marker_1_array.astype(int)

    marker_1 = property(_get_marker_1, _set_marker_1)

    def _get_marker_2(self):
        """
        Get or set the marker_1 of the waveform
        - marker_1 (numpy array)
        """
        return self._marker_2

    def _set_marker_2(self, marker_2_array):
        if not self._length:
            self._length = len(marker_2_array)
        elif self._length != len(marker_2_array):
            raise AttributeError('trying to set marker_2 of unexpected length')
        elif not isinstance(marker_2_array, np.ndarray):
            raise AttributeError('marker_2 must be numpy array')
        elif any(int(m) not in [0, 1] for m in marker_2_array):
            raise AttributeError('marker_2 values not in (0, 1)')
        self._marker_2 = marker_2_array.astype(int)

    marker_2 = property(_get_marker_2, _set_marker_2)

    # def __setattr__(self, name, value):
    # if name not in ('wave', 'marker_1', 'marker_2','length'):
    #     raise AttributeError('attribute %s not allowed' % name)
    # else:
    #     super().__setattr__(name, value)
