import numpy as np
import copy
import matplotlib.pyplot as plt
from . import Segment

# TODO: exception types
# TODO: docstrings
# TODO: sort out setting sample rate between segment and waveform
# TODO: write check
# TODO: write clear (markers and segments)
# TODO: write function for inserting segment into specific position


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
        elif self.segment_list is not None:
            return sum(s.duration for s in self.segment_list
                       if s.duration is not None)
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

    # def check(self):
    #     """
    #     Function which checks that the wave and markers are all set

    #     nb doesn't check that they are all the same length because
    #     it should b impossible to make them otherwise
    #     """
    #     unset = []
    #     if self.wave is None:
    #         unset.append('wave')
    #     if self.marker_1 is None:
    #         unset.append('marker_1')
    #     if self.marker_2 is None:
    #         unset.append('marker_2')
    #     if len(unset) > 0:
    #         raise Exception(
    #             'must specify non None array for {}'.format(", ".join(unset)))
    # return True

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
        markers = {1: np.zeros(len(self), dtype=int),
                   2: np.zeros(len(self), dtype=int)}

        if self.segment_list is not None:
            for i in [1, 2]:
                start = 0
                for seg in self.segment_list:
                    for j, delay in enumerate(seg.markers[i]['delay_points']):
                        duration = seg.markers[i]['duration_points'][j]
                        markers[i][
                            (start + delay): (start + duration + delay)] = 1
                    start += len(seg)
        if self._markers is not None:
            for i in [1, 2]:
                for j, delay in enumerate(self._markers[i]['delay_points']):
                    duration = self._markers[i]['duration_points'][j]
                    markers[i][delay:(duration + delay)] = 1
        return markers

    markers = property(fget=_get_markers)

    def add_marker(self, marker_num, delay, duration):
        if self.wave is None:
            raise Exception('cannot set marker before setting wave')
        elif len(self.wave) < (delay + duration):
            raise Exception('end of marker is beyond end of wave')
        elif marker_num not in [1, 2]:
            raise Exception('marker number not in (1, 2)')
        elif not all(type(d) is int for d in [delay, duration]):
            raise TypeError('delay and duration must be integers as they'
                            ' are numbers of points')
        if self._markers is None:
            self._markers = {1: {'delay_points': [],
                                 'duration_points': []},
                             2: {'delay_points': [],
                                 'duration_points': []}}
        self._markers[marker_num]['delay_points'].append(delay)
        self._markers[marker_num]['duration_points'].append(duration)

    def clear_wave_markers(self):
        self._markers = None

    def clear_all_markers(self):
        self._markers = None
        if self.segment_list:
            for s in self.segment_list:
                s.clear_markers()

    def add_segment(self, segment, position=None):
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
            elif position is None:
                self.segment_list.append(segment)
            else:
                self.segment_list.insert(position, segment)
        elif position is not None:
            raise Exception('Cannot insert segment into indexed position'
                            ' if the waveform is not defined by a segment '
                            'list')
        else:
            np.append(self._wave, segment.points)
            np.append(self._marker_1, np.zeros(len(segment)))
            np.append(self._marker_2, np.zeros(len(segment)))

    def copy(self):
        return copy.deepcopy(self)

    def plot(self, subplot=None):
        if subplot is None:
            fig, ax = plt.subplots()
        else:
            ax = subplot
        if self.channel is not None:
            ax.set_title('Channel {}'.format(self.channel))
        ax.set_ylim([-1.1, 1.1])
        ax.plot(self.wave, lw=1,
                color='#009FFF', label='wave')
        ax.plot(self.markers[1], lw=1,
                color='#008B45', alpha=0.6, label='m1')
        ax.plot(self.markers[2], lw=1,
                color='#FE6447', alpha=0.6, label='m2')
        ax.legend(loc='upper right', fontsize=10)
        if subplot is None:
            return fig
        else:
            return ax
