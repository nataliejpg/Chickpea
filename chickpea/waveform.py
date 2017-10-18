import numpy as np
import math
import copy
import logging
import warnings

try:
    import matplotlib.pyplot as plt
except RuntimeError as e:
    warnings.warn('Could not import matplotlib {}'.format(e))

from . import Segment

log = logging.getLogger(__name__)


class Waveform:
    """
    Waveform class which represents the wave and markers
    (as numpy arrays) for one channel of an AWG at one point in time.
    ie one element has many waveforms (one per channel)
    """

    def __init__(self, length: int=None, channel: int=None,
                 segment_list: list=None, sample_rate: float=None):
        """
        Args:
            length: optional number of points
            channel: optional channel to assign to when in an element
            segment_list: optional list of segments from which waveform
                is built
            sample_rate: optional sample rate which will set the SR of all
                segments or just be used as an fyi attribute
        """

        self.channel = channel
        if length is not None and segment_list is None:
            self._wave = np.zeros(int(length))
        elif length is not None:
            raise RuntimeError('Cannot set length and segment list')
        else:
            self._wave = None
        self._markers = None

        self.segment_list = copy.deepcopy(segment_list)
        if sample_rate is not None:
            self.sample_rate = sample_rate
        else:
            self._sample_rate = None

    def _get_duration(self):
        try:
            segment_durations = [s.duration for s in self.segment_list]
            return math.fsum(segment_durations)
        except Exception as e:
            pass
            if self.sample_rate is None:
                raise RuntimeError(
                    'Could not get duration from segment list({}) and'
                    ' sample rate not set on waveform')
            return len(self) / self.sample_rate

    duration = property(fget=_get_duration)

    def _set_sample_rate(self, val):
        if self.segment_list is not None:
            for s in self.segment_list:
                s.func_args['SR'] = val
        self._sample_rate = val

    def _get_sample_rate(self):
        return self._sample_rate

    sample_rate = property(fget=_get_sample_rate, fset=_set_sample_rate)

    def check(self):
        """
        Checks:
        1) wave is not none
        2) if segments present they all have a duration
        2) if segments present that sum of thier durations is same as that
            of wave
        """
        if self.wave is None:
            raise RuntimeError('Wave is None')
        if self.segment_list is not None:
            try:
                segments_dur = math.fsum(
                    [s.duration for s in self.segment_list])
            except Exception as e:
                raise RuntimeError('segment_list present but failed to get '
                                   'duration for all segments: {}'.format(e))
            if segments_dur != self.duration:
                raise RuntimeError('duration of segments not equal to duration'
                                   ' of wave {} != {}'.format(
                                       segments_dur, self.duration))
        return True

    def __len__(self):
        try:
            wave = self.wave
        except Exception as e:
            raise RuntimeError('Could not get wave to evaluate '
                               'length: {}'.format(e))
        if wave is None:
            raise RuntimeError('wave is None, cannot get length')
        return len(self.wave)

    def _get_wave(self):
        if self.segment_list is not None:
            return np.concatenate([s.points for s in self.segment_list])
        else:
            return self._wave

    def _set_wave(self, wave_array: np.ndarray):
        self.segment_list = None
        self._wave = wave_array

    wave = property(_get_wave, _set_wave)

    def _get_markers(self):
        """
        Function which gets wave markers and segment markers both specified
        in delay and duration points. These are summed XOR and converted to
        arrays of 1 and 0 of same length as wave.

        Returns:
            marker dict of form {1: [], 2: []}
        """
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

    def add_marker(self, marker_num: int, delay: int, duration: int):
        """
        Args:
            marker_num: 1 or 2
            delay: number of points from start of wave
            duration: number of points for marker to be on for
        """
        if self.wave is None:
            raise RuntimeError('cannot set marker before setting wave')
        elif len(self.wave) < (delay + duration):
            raise RuntimeError('end of marker is beyond end of wave')
        elif marker_num not in [1, 2]:
            raise RuntimeError('marker number not in (1, 2)')
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
        """
        Clears markers associated with the wave.
        """
        self._markers = None

    def clear_segment_markers(self):
        """
        Clears bound markeres on constituent segments of the Waveform.
        """
        if self.segment_list:
            for s in self.segment_list:
                s.clear_markers()

    def clear_all_markers(self):
        self.clear_wave_markers()
        self.clear_segment_markers()

    def add_segment(self, segment, position: int = None):
        """
        Adds a segment to the segment list and updates marker lists and
        wave as necessary

        Args:
            segment
            position (int) (default None): position in segment list for segment
                to be added
        """
        if not isinstance(segment, Segment):
            raise TypeError('cannot add segment not of type Segment')
        if self.sample_rate is not None:
            if "SR" not in segment.func_args:
                segment.func_args["SR"] = self.sample_rate
            elif segment.func_args["SR"] != self.sample_rate:
                raise RuntimeError('Cannot add a segment with a different'
                                   'SR in func_args to that of the waveform. '
                                   'waveform SR: {}, segment SR: {}'.format(
                                       self.sample_rate,
                                       segment.func_args["SR"]))
        if self._wave is None:
            if self.segment_list is None:
                self.segment_list = [segment]
            elif position is None:
                self.segment_list.append(segment)
            else:
                self.segment_list.insert(position, segment)
        elif position is not None:
            raise RuntimeError('Cannot insert segment into indexed position'
                               ' if the waveform is not defined by a segment '
                               'list')
        else:
            for i in [1, 2]:
                delays = np.array(segment.markers[i]['delay_points'])
                durations = segment.markers[i]['duration_points']
                new_delays = list(delays + len(self.wave))
                self._markers[i]['delay_points'].append(new_delays)
                self._markers[i]['duration_points'].append(durations)
            np.append(self._wave, segment.points)

    def copy(self):
        return copy.deepcopy(self)

    def plot(self, subplot=None):
        """
        Plots the wave and markers in a matplotlib.pyplot subplot

        Args:
            subplot to plot on, otherwise makes a new figure

        Returns:
            plot
        """
        if subplot is None:
            try:
                fig, ax = plt.subplots()
            except NameError as e:
                raise Warning('Could not create matplot figure {}'.format(e))
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
