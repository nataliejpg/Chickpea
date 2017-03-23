import numpy as np

# TODO: exception types


class Waveform:
    def __init__(self, length=None, channel=None, segment_list=[]):
        """
        Waveform class which represents the wave and markers
        (as numpy arrays) for one channel
        of the AWG at one point in time.
        ie one element has many waveforms (one per channel)

        Args:
            length (int): optional number of points
            channel (int): optional channel to assign to when in an element
            segment_list (list): optional list of segments from which waveform
                is built
        """

        if channel:
            self.channel = channel
        else:
            self._channel = None
        if length:
            # self._length = int(length)
            self._wave = np.zeros(int(length))
            self._marker_1 = np.zeros(int(length))
            self._marker_2 = np.zeros(int(length))
        else:
            # self._length = None
            self._wave = None
            self._marker_1 = []
            self._marker_2 = []

        self._segment_list = segment_list

    # def clear(self):
    #     """
    #     Function which sets the wave and markers of the waveform to zeros
    #     """
    #     self._wave = None
    #     self._marker_1 = None
    #     self._marker_2 = None

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
            unset.append('marker_1')
        if self._marker_2 is None:
            unset.append('marker_2')
        if len(unset) > 0:
            raise Exception(
                'must specify non None array for {}'.format(", ".join(unset)))
        return True

    def _get_channel(self):
        """
        Get or set the channel of the waveform

        Returns:
            channel (int)
        """
        return self._channel

    def _set_channel(self, value):
        if not isinstance(value, int):
            raise Exception('channel must be integer')
        self._channel = value

    channel = property(_get_channel, _set_channel)



    def __len__(self):
        self._length = len(self.wave)
        return(self._length)

    def _get_wave(self):
        """
        Get or set the wave of the waveform

        Returns:
            wave (numpy array)
        """
        if self._segment_list:
            return np.concatenate([s.points for s in self._segment_list])
        else:
            return self._wave

    def _set_wave(self, wave_array):
        """
        Function which sets the wave and clears the markers if necessary

        Args:
            wave_array (numpy array)
        """
        if not isinstance(wave_array, np.ndarray):
            raise TypeError('wave must be numpy array')
        self._segment_list.clear()

        if ((self.marker_1 or self.marker_2) and
                len(wave_array) != len(self._wave)):
            # if not self._length:
            #     self._length = len(wave_array)
            # elif self._length != len(wave_array):
            #     print('new wave array is of different length to old, '
            #           'clearing markers')
            self._marker_1.clear()
            self._marker_2.clear()
        self._wave = wave_array

    wave = property(_get_wave, _set_wave)

    def _get_marker_1(self):
        """
        Gets the marker_1 of the waveform

        Returns:
            marker_1 (list)
        """
        if (self._wave is None) and not self.segment_list:
            raise Exception('wave must be set for marker to be gettable')
        if (self._marker_1 is not None) and len(self._marker_1) > 0:
            return self._marker_1
            marker = np.zeros(self._length)

        if self.from_segments:
            start_index = 0
            for seg in self.segment_list:
                start_index += len(seg)
                for i, delay in enumerate(seg.markers[1]['delays']):
                    duration = seg.markers[1]['durations'][i]
                    marker[(start_index + delay): (duration + delay)] = 1
        else:
            marker = self._marker_1
        return marker

    def _set_marker_1(self, marker_1_array):
        if not self._length:
            self._length = len(marker_1_array)
        elif self._length != len(marker_1_array):
            raise Exception('trying to set marker_1 of unexpected length')
        elif not isinstance(marker_1_array, np.ndarray):
            raise Exception('marker_1 must be numpy array')
        elif any(int(m) not in [0, 1] for m in marker_1_array):
            raise Exception('marker_1 values not in (0, 1)')
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
            raise Exception('trying to set marker_2 of unexpected length')
        elif not isinstance(marker_2_array, np.ndarray):
            raise Exception('marker_2 must be numpy array')
        elif any(int(m) not in [0, 1] for m in marker_2_array):
            raise Exception('marker_2 values not in (0, 1)')
        self._marker_2 = marker_2_array.astype(int)

    marker_2 = property(_get_marker_2, _set_marker_2)

    def add_segment(self, segment):
        """
        """
        if self.from_segments or self._wave:
            self.from_segments = True
            self._segment_list.append(segment)
        else:
            np.append(self._wave, segment.points)
            np.append(self._marker_1, np.zeros(len(segment)))
            np.append(self._marker_1, np.zeros(len(segment)))
