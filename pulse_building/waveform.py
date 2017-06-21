import numpy as np
from . import Segment

# TODO: exception types
# TODO: docstrings
# TODO: sort out setting sample rate between segment and waveform


class Waveform:
    def __init__(self, length=None, channel=None, segment_list=None,
                 sample_rate=None):
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
            self._wave = np.zeros(int(length))
            self._markers = {1: np.zeros(int(length)),
                             2: np.zeros(int(length))}
        else:
            self._wave = None
            self._markers = None

        self.segment_list = segment_list
        self._sample_rate = sample_rate
        if self._sample_rate is not None:
            self._set_sample_rate(sample_rate)

    def _get_duration(self):
        if self._sample_rate is None:
            raise Exception('Cannot get duration as sample_rate is None')
        else:
            return len(self) / self._sample_rate

    duration = property(fget=_get_duration)

    def _set_sample_rate(self, val):
        if self.segment_list is not None:
            for s in self.segment_list:
                s.func_args['SR'] = val
        self._sample_rate = val

    def _get_sample_rate(self):
        return self._sample_rate

    sample_rate = property(fget=_get_sample_rate, fset=_set_sample_rate)

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
        if self.wave is None:
            unset.append('wave')
        if self.marker_1 is None:
            unset.append('marker_1')
        if self.marker_2 is None:
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
        if self.wave is None:
            raise Exception('wave is None, cannot get length')
        return(len(self.wave))

    def _get_wave(self):
        """
        Get or set the wave of the waveform

        Returns:
            wave (numpy array)
        """
        if self.segment_list is not None:
            return np.concatenate([s.points for s in self.segment_list])
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
        self.segment_list = None

        if (self._wave is None) or (len(wave_array) != len(self._wave)):
            self._marker_1 = np.zeros(len(wave_array))
            self._marker_2 = np.zeros(len(wave_array))
        self._wave = wave_array

    wave = property(_get_wave, _set_wave)

    def _get_markers(self):
        """
        Gets the marker_1 of the waveform

        Returns:
            marker_1 (list)
        """
        # if (self._wave is None) and not self.segment_list:
        #     raise Exception('wave must be set for marker to be gettable')
        # if self._marker_1 is not None:
        #     return self._marker_1
        markers = {1: np.zeros(len(self)), 2: np.zeros(len(self))}

        if (self._markers is None) and (self.segment_list is not None):
            for i in [1, 2]:
                start_index = 0
                for seg in self.segment_list:
                    start_index += len(seg)
                    for j, delay in enumerate(seg.markers[1]['delay_points']):
                        duration = seg.markers[1]['duration_points'][j]
                        markers[i][
                            (start_index + delay): (duration + delay)] = 1
        else:
            markers = self._markers
        return markers

    markers = property(fget=_get_markers)

    def add_marker_on(self, marker_num, start, stop):
        if self.wave is None:
            raise Exception('cannot set marker before setting wave')
        elif len(self.wave) < stop:
            raise Exception('end of marker is beyond end of wave')
        elif marker_num not in [0, 1]:
            raise Exception('marker number not in (0, 1)')
        if (self.segment_list is not None) and (self._markers is None):
            print('Warning: Manually setting a marker on waveform will '
                  'disregard any markers set on segments')
        if self._markers is None:
            self._markers = {1: np.zeros(int(len(self))),
                             2: np.zeros(int(len(self)))}
        self._markers[marker_num][start:stop] = 1

    def set_marker_array(self, marker_num, marker_array):
        if self.wave is None:
            raise Exception('cannot set marker before setting wave')
        elif len(self.wave) != len(marker_array):
            raise Exception('trying to set marker_1 of unexpected length')
        elif not isinstance(marker_array, np.ndarray):
            raise Exception('marker must be numpy array')
        elif any(int(m) not in [0, 1] for m in marker_array):
            raise Exception('marker values not in (0, 1)')
        elif marker_num not in [0, 1]:
            raise Exception('marker number not in (0, 1)')
        if self.segment_list is not None:
            print('Warning: Manually setting a marker on waveform will '
                  'disregard any markers set on segments')
        self._markers[marker_num] = marker_array.astype(int)

    def add_segment(self, segment):
        """
        """
        if not isinstance(segment, Segment):
            raise TypeError('cannot add segment not of type Segment')
        if self._sample_rate is not None:
            if "SR" not in segment.func_args:
                segment.func_args["SR"] = self._sample_rate
            elif segment.func_args["SR"] != self.sample_rate:
                raise ValueError('Cannot add a segment with a different'
                                 'SR in func_args to that of the waveform. '
                                 'waveform SR: {}, segment SR: {}'.format(
                                     self._sample_rate,
                                     segment.func_args["SR"]))
        if self._wave is None:
            if self.segment_list is None:
                self.segment_list = [segment]
            else:
                self.segment_list.append(segment)
        else:
            np.append(self._wave, segment.points)
            np.append(self._marker_1, np.zeros(len(segment)))
            np.append(self._marker_2, np.zeros(len(segment)))

    def copy(self):
        new_waveform = Waveform(channel=self.channel,
                                segment_list=self.segment_list)
        if self.segment_list is None:
            new_waveform.wave = self.wave
            new_waveform.marker_1 = self.marker_1
            new_waveform.marker_2 = self.marker_2
        return new_waveform
