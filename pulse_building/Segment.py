import numpy as np

# TODO: right exceptions
# TODO: cut name?
# TODO: unbound and bound markers coexisting happily?


class Segment:
    def __init__(self, name=None, gen_func=None, func_args={},
                 sample_rate=None, points_array=None, points_markers={},
                 time_markers={}, raw_markers={}):
        """
        Segment class which represents a segment of a wave and markers
        for one channel of the AWG at one point in time. These can be in
        the form of an explicit numpy array or generated by functions
        together with a sampling rate.
        ie one waveform has many segments

        Args:
            name (str): optional segment name
            gen_func(fn): optional function used to generate segment points,
                must have SR sample rate as a parameter
            func_args (dict): optional dict of arguments to go into the
                function alongside sample rate
            sample_rate (float): optional sample rate to be passed to the
                function when points are generated, needs to be specified
                before getting points if points are generated from funtion
            points_array (list or numpy array): optional alternative to have a
                segment generated by a function.
            points_markers (dict): optional dictionary of bound markers of the
                form {1: {'delay_points': [], 'duration_points': []}, 2: ...}
                (ie values in points rather than time)
            time_markers (dict): optional dictionary of bound markers
                of the form {1: {'delays': [], 'durations': []}, 2: ...}
            raw_markers (dict): optional dictionary of form {1: [], 2: []]}
                where the length of the marker lists must be 0 or the same as
                the specified points_array
        """

        # Checks if there is a points array specified or a function specified
        # and takes the function name for naming the segment
        if points_array is not None:
            if gen_func is not None:
                raise Exception('cannot set both gen_func for points '
                                'generation and points_array')
            elif not isinstance(points_array, (list, np.ndarray)):
                raise TypeError('points_array must be a list or numpy array')
        else:
            if (gen_func is not None) and (name is None):
                name = gen_func.__name__

        # Checks marker dictionaties have valid keys, that if a marker is
        # specified it is not duplicated across dictionaries and that any
        # raw markers  are of the same length as the specified points array.
        if not all([k in [1, 2] for k in points_markers.keys()]):
            raise Exception('points_markers dict must have keys in [1, 2]'
                            ' {} received'.format(points_markers.keys()))
        if not all([k in [1, 2] for k in time_markers.keys()]):
            raise Exception('time_markers dict must have keys in [1, 2]'
                            ' {} received'.format(time_markers.keys()))
        if not all([k in [1, 2] for k in raw_markers.keys()]):
            raise Exception('raw_markers dict must have keys in [1, 2]'
                            ' {} received'.format(raw_markers.keys()))

        time_markers_nums = list(time_markers.keys())
        points_marker_nums = list(points_markers.keys())
        raw_marker_nums = list(raw_markers.keys())
        overlap = set.intersection(time_markers_nums,
                                   points_marker_nums,
                                   raw_marker_nums)
        if overlap:
            raise Exception('you have tried to set a value for marker(s) {} '
                            'in more than one of the dictionaries: '
                            'time_markers, points_markers,'
                            ' raw_markers'.format(overlap))
        for m in time_markers_nums:
            if not list(time_markers[m].keys()) is ['delays', 'durations']:
                raise Exception('time_markers[{}] must have keys '
                                '[\'delays\', \'durations\'], received'
                                ': {}'.format(m, time_markers[m].keys()))
        for m in points_marker_nums:
            if (not list(points_markers[m].keys())
                    is ['delay_points', 'duration_points']):
                raise Exception('points_markers[{}] must have keys '
                                '[\'delay_points\', '
                                '\'duration_points\'], received'
                                ': {}'.format(m,
                                              points_markers[m].keys()))
        for m in raw_marker_nums:
            if not isinstance(raw_markers[m], (list, np.ndarray)):
                raise TypeError('raw_markers[{}] must be a list or numpy '
                                'array'.format(m))
            elif points_array is None:
                raise Exception('must set points_array to set raw_markers')
            elif len(raw_markers[m]) != len(points_array):
                raise Exception('raw_markers[{}] length {} not equal to '
                                'points_array length {}'.format(
                                    m,
                                    len(raw_markers[m]),
                                    len(points_array)))
            points_markers.update(self.raw_to_points(raw_markers))

        self.name = name
        self.sample_rate = sample_rate
        self.func = gen_func
        self.func_args = func_args
        self._points = np.array(points_array)
        self._points_markers = points_markers
        self._time_markers = time_markers

    def __iter__(self):
        return iter(self.points)

    def __len__(self):
        return len(self.points)

    def __add__(self, other):
        """
        Function for addition or concatenation of segments which returns
        a Segment object with
        name: 'seg1name_seg2name'
        gen_func: None
        func_args: {}
        sample_rate: dependent on sample_rates of segments (uncontested SR if
            any are present, otherwise None)
        points_array: np.array(seg1points, seg2points)
        points_markers: markers from both segments converted into delay and
            duration values in points
        time_markers: {}
        raw_markers: {}

        Args:
            other (Segment): second segment for addition

        Returns:
            sum  of semgments (Segment)
        """
        if not isinstance(other, Segment):
            raise ValueError('Segment can only be added to another Segment.'
                             'Received object of type {}'.format(type(other)))

        new_name = self.name + '_' + other.name

        # If both sample rates not set: set the new sample rate
        # to be the non None sample rate or None if both are None
        if all([self.sample_rate, other.sample_rate]):
            new_sample_rate = self.sample_rate or other.sample_rate
        # If both sample rates are set: check they are the same
        elif self.sample_rate != other.sample_rate:
            raise Exception('sample rates of segments do not match')
        else:
            new_sample_rate = self.sample_rate

        new_points = np.concatenate([self.points, other.points])

        new_markers = {1: {}, 2: {}}

        for m in [1, 2]:
            new_marker_delays = np.append(
                self.markers[m]['delays'],
                other.markers[m]['delays'] + len(self))
            new_marker_durations = np.append(
                self.markers[m]['durations'],
                other.markers[m]['durations'])
            new_markers[m]['delays'] = new_marker_delays
            new_markers[m]['durations'] = new_marker_durations

        return Segment(name=new_name, sample_rate=new_sample_rate,
                       points_array=new_points, points_markers=new_markers)

    def _set_points(self, points_array):
        """
        Function which sets the points specifying the segment. The
        generator function is set to None and any unbound markers with
        a different length are cleared. Sample rate is also set to None
        and the function arguments dictionary cleared.

        Args:
            points_array (numpy array): points specifying the segment
        """
        if not isinstance(points_array, np.ndarray):
            raise AttributeError('points must be numpy array')
        for m in [1, 2]:
            if len(self._unbound_markers[m]) != len(points_array):
                del self._unbound_markers[m]
        self.sample_rate = None
        self.func = None
        self.func_args.clear()
        self._points = points_array

    def _get_points(self):
        """
        Function which gets the points of a segment either by returning the
        array if specified or by evaluating the function with the given
        sample rate.

        Returns:
            points_array (numpy array): points specifying the segment
        """
        if self._points is not None:
            return self._points
        elif self.func is None:
            raise Exception('if points not set explicitly function must'
                            'be set to generate segment points')
        elif self.sample_rate is None:
            raise Exception('sample rate not set so segment points cannot '
                            'be generated by function')
        else:
            return self.func(SR=self.sample_rate, **self.func_args)

    points = property(fget=_get_points, fset=_set_points)

    def _get_duration(self):
        """
        Function which gets the duration of the segment from the sample
        rate and length of points array
        """
        if self.sample_rate is None:
            raise Exception('cannot get duration if no sample rate set')
        else:
            return len(self) / self.sample_rate

    duration = property(fget=_get_duration)

    def _get_markers(self):
        """
        Function which returns a dictionary of marker delays and durations
        specified in points relative to the start of the segment points

        Returns:
            markers_dict of the form
                {1: {'delay_points': [], 'duration_points': []},
                 2: {'delay_points': [], 'duration_points': []}}
        """
        markers_dict = self._points_markers
        if self._time_markers:
            if self.sample_rate is None:
                raise Exception('sample rate not set so bound segment'
                                'markers specified in time '
                                'cannot be calculated')
            markers_dict.update(self.time_to_points(self._time_markers,
                                                    self.sample_rate))
        return markers_dict

    markers = property(fget=_get_markers)

    def add_bound_markers(self, marker_num, delay_duration_list, time=False):
        """
        Function which adds a bound marker to a segment by updating the
        relevant marker dictionary with delay and duration values.

        Args:
            marker_num (1 or 2): marker to add to
            delay_duration_list (list or numpy array): list of delay-duration
                pairs specifying the start and duration that the marker should
                be 'on' for
            time (bool): whether or not values are in real time or in number
                of points(default False)
        """
        if not (marker_num in [1, 2]):
            raise Exception('marker_num be in [1, 2]: '
                            'received {}'.format(marker_num))
        if not isinstance(delay_duration_list, (list, np.ndarray)):
            raise AttributeError('delay_duration_list must be a'
                                 ' list or numpy array')
        delay_duration_array = np.array(delay_duration_list)
        if not (delay_duration_array.shape[1] == 2):
            raise AttributeError('delay_duration_list must have shape (n, 2)'
                                 'so that delay from segment start and '
                                 'duration is set for each')

        if time:
            try:
                del self._points_markers[marker_num]
            except KeyError:
                pass
            try:
                old_delay_vals = self._time_markers[marker_num]['delays']
                old_duration_vals = self._time_markers[marker_num]['durations']
            except KeyError:
                old_delay_vals = []
                old_duration_vals = []
                self._points_markers[marker_num] = {}
            new_delay_vals = np.append(old_delay_vals,
                                       delay_duration_array[:, 0])
            new_duration_vals = np.append(old_duration_vals,
                                          delay_duration_array[:, 1])

            self._time_markers[marker_num]['delays'] = new_delay_vals
            self._time_markers[marker_num]['durations'] = new_duration_vals

        else:
            try:
                del self._time_markers[marker_num]
            except KeyError:
                pass
            try:
                old_delay_vals = self._points_markers[
                    marker_num]['delay_points']
                old_duration_vals = self._points_markers[
                    marker_num]['delay_points']
            except KeyError:
                old_delay_vals = []
                old_duration_vals = []
                self._points_markers[marker_num] = {}
            new_delay_vals = np.append(old_delay_vals,
                                       delay_duration_array[:, 0])
            new_duration_vals = np.append(old_duration_vals,
                                          delay_duration_array[:, 1])

            self._points_markers[marker_num]['delay_points'] = new_delay_vals
            self._points_markers[marker_num][
                'duration_points'] = new_duration_vals

    def add_raw_marker(self, marker_num, marker_array):
        """
        Function which adds a raw marker array to the segment by converting
        it into a delay-duration values in points

        Args:
            marker_num (1 or 2): marker to update
            marker_array (list or numpy array): list of 0s and 1s of the
                same length as the segmen specifying marker on/off state
        """
        if not (marker_num in [1, 2]):
            raise Exception('marker_num be in [1, 2]: '
                            'received {}'.format(marker_num))
        elif not isinstance(marker_array, (list, np.ndarray)):
            raise TypeError('marker_array must be numpy array')
        elif self._points_array is None:
            raise Exception('must set points to set raw_markers')
        elif len(marker_array) != len(self._points_array):
            raise Exception('marker_array length {} not equal to '
                            'points_array length {}'.format(
                                len(marker_array),
                                len(self._points_array)))
        elif any(int(v) not in [0, 1] for v in marker_array):
            raise AttributeError('marker values not in (0, 1)')
        try:
            del self._time_markers[marker_num]
        except KeyError:
            pass
        raw_marker = {marker_num: np.array(marker_array)}
        self._points_markers.update(self.raw_to_points(raw_marker))

    def clear_markers(self):
        """
        Function which clears marker dictionaries
        """
        self._points_markers.clear()
        self._time_markers.clear()

    @staticmethod
    def raw_to_points(raw_markers):
        """
        Function which converts a dictionary of raw marker arrays into
        a dictionary of markers specified in duration and delay of marker
        'on' state

        Args:
            raw_markers (dict) of the form {1: [], 2: []]}

        Returns:
            points_markers (dict) of ther form
        """
        points_markers = {}
        for m in np.array(raw_markers):
            nonzero_indices = np.nonzero(raw_markers[m])[0]
            starts = np.array([s for s in nonzero_indices
                               if raw_markers[m][s - 1] != 1])
            ends = np.array([s for s in nonzero_indices
                             if raw_markers[m][s + 1] != 1])
            marker_delays = starts
            marker_durations = ends - starts
            points_markers[m]['delay_points'] = marker_delays
            points_markers[m]['duration_points'] = marker_durations
        return points_markers

    @staticmethod
    def time_to_points(time_markers, sample_rate):
        """
        Function which converts a dictionary of marker delays and durations
        in time into one specified in points

        Args:
            time_markers (dict) of the form
                {1: {'delays': [], 'durations': []}, 2: ...}
            sample_rate (float): points per second value

        Returns:
            points_markers (dict) of the form
                {1: {'delay_points': [], 'duration_points': []}, 2: ...}
        """
        points_markers = {}
        for m in time_markers:
            marker_delays = (time_markers[m][:, 0] *
                             sample_rate)
            marker_durations = (time_markers[m][:, 1] *
                                sample_rate)
            points_markers[m]['delay_points'] = marker_delays
            points_markers[m]['duration_points'] = marker_durations
        return points_markers
