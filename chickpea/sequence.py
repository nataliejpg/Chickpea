import numpy as np
import copy
import os
from typing import Union, List, Tuple
from . import Segment, Waveform, Element

# TODO: write tests (for all)
# TODO: test wrap

setting_options = Union[int, List[int], np.ndarray]


class Sequence:
    def __init__(self, name: str = None, variable: str = None,
                 variable_label: str = None, variable_unit: str = None,
                 start: float = None, stop: float = None, step: float = None,
                 nreps: setting_options =1, trig_waits: setting_options = 0,
                 goto_states: setting_options = 0,
                 jump_tos: setting_options = 1, labels: dict = None,
                 sample_rate: float = None):
        """
        Sequence class which represents a list of elements to run in order on
        an AWG with optional metadata information.
        ie one sequence has many elements

        Args:
            name: optional human readable identifier
            variable: optional name of the pyhsical variable varied
                            in each slemen of the sequence
            variable_unit: unit of the variable
            start: optional starting value of the variable
                           ie the value in elements[0]
            stop: optional finishing value of the variable
                          ie the value in elements[-1]
            step: optional step value of the variable
            nreps: number of times each element should be repeated
                                default 1
            trig_waits: trigger wait state for each element
                        default 0
            goto_states: element to jump to after each element has
                        finished (AWG indexing starts from 1)
                        0 means jump to next, this is the default
            jump_tos: 'jump state' of each element (0: off, 1: on)
                      default 1
            labels (dict): user defined metadata
            sample_rate attribute
        """

        self._elements = []
        self.nreps = nreps
        self.trig_waits = trig_waits
        self.goto_states = goto_states
        self.jump_tos = jump_tos
        self.name = name
        self.variable = variable
        self.variable_label = variable_label or variable
        self.variable_unit = variable_unit
        self.labels = labels or {}
        if any(s is not None for s in [start, stop, step]):
            if not all(isinstance(s, (float, int))
                       for s in [start, stop, step]):
                raise TypeError('start, stop and step must either all be '
                                'set as numbers (floats or ints) or none set')
        self._start = start
        self._stop = stop
        self._step = step
        self.sample_rate = sample_rate

    def __getitem__(self, key: int):
        return self._elements[key]

    def __setitem__(self, key: int, value: Element):
        self._elements[key] = value

    def __repr__(self):
        return repr(self._elements)

    def __len__(self):
        return len(self._elements)

    def __delitem__(self, key: int):
        del self._elements[key]

    def __cmp__(self, lst):
        return cmp(self._elements, lst)

    def __contains__(self, item: Element):
        return item in self._elements

    def __iter__(self):
        return iter(self._elements)

    def _set_sample_rate(self, val: float):
        if self._elements:
            for e in self._elements:
                e.sample_rate = val
        self._sample_rate = val

    def _get_sample_rate(self):
        return self._sample_rate

    sample_rate = property(fget=_get_sample_rate, fset=_set_sample_rate)

    @property
    def start(self):
        return self._start

    @property
    def stop(self):
        return self._stop

    @property
    def step(self):
        return self._step

    @property
    def variable_array(self):
        if any(s is None for s in [self._start, self._stop, self._step]):
            return None
        else:
            number = int(round(abs(self._stop - self._start) / self._step + 1))
            return np.linspace(self._start, self._stop, num=number)

    @property
    def duration(self):
        return sum(e.duration for e in self._elements)

    def add_element(self, element: Element, position: int =None):
        """
        Function which adds an Element to the elements list

        Args:
            Element
            position to insert element in list (default at end)
        """
        if self.sample_rate is not None:
            if element.sample_rate is None:
                element.sample_rate = self.sample_rate
            elif element.sample_rate != self.sample_rate:
                raise ValueError('Cannot add a element with a different'
                                 'sample rate to that of the sequence. '
                                 'element SR: {}, sequence SR: {}'.format(
                                     element.sample_rate, self.sample_rate))
        if position is not None:
            self._elements.insert(position, element)
        else:
            self._elements.append(element)

    def clear(self):
        """
        Functions which deletes contents of elements and variables lists
        sets stored values to None
        """
        del self._elements[:]
        del self.trig_waits[:]
        del self.nreps[:]
        del self.goto_states[:]
        del self.jump_tos[:]
        self.name = None
        self.variable = None
        self.variable_unit = None
        self._start = None
        self._stop = None
        self._step = None

    def _get_channels_used(self, element_index=0):
        """
        Function which calculates the channels used on an element

        Args:
            - element_index (int): default 0 (first element)

        Returns:
            - list of channels used
        """
        chans = list(self._elements[element_index].keys())
        return chans

    def unwrap(self):
        """
        Function which unwraps the sequence into a tuple of lists which
        are the inputs for the Tektronix_AWG5014 qcodes instument_driver
        make_send_and_load_awg_file function.

        Returns:
            - tuple of (waves, m1s, m2s, nreps, trig_waits,
               goto_states, jump_tos, channels)

               waves is of the form:
               [[wfm1ch1, wfm2ch1, ...], [wfm1ch2, wfm2ch2], ...]
               as are m1s and m2s

               channels is of the form [ch1, ch3]

               all others are arrays of the same length as the sequence
        """
        chan_list = self._get_channels_used()
        awg_ch_dict = {}
        wf_dict = {}
        m1_dict = {}
        m2_dict = {}
        for chan in chan_list:
            awg, channel = divmod(chan, 4)
            if awg not in awg_ch_dict:
                awg_ch_dict[awg] = []
            awg_ch_dict[awg].append(channel)
        for awg, ch_list in awg_ch_dict.iteritems():
            chan_list.sort()
            wf_dict[awg] = [[] for c in ch_list]
            m1_dict[awg] = [[] for c in ch_list]
            m2_dict[awg] = [[] for c in ch_list]

        for element in self._elements:
            for awg, ch_list in awg_ch_dict.iteritems():
                for i, ch in enumerate(ch_list):
                    wf_dict[awg][i].append(element[ch].wave)
                    m1_dict[awg][i].append(element[ch].markers[1])
                    m2_dict[awg][i].append(element[ch].markers[2])
        if isinstance(self.nreps, int):
            nrep_list = [self.nreps] * len(self._elements)
        else:
            nrep_list = self.nreps
        if isinstance(self.trig_waits, int):
            trig_wait_list = [self.trig_waits] * len(self._elements)
        else:
            trig_wait_list = self.trig_waits
        if isinstance(self.goto_states, int):
            goto_state_list = np.arange(len(self._elements)) + 2
            goto_state_list[-1] = 1
        else:
            goto_state_list = self.goto_states
        if isinstance(self.jump_tos, int):
            jump_to_list = [self.jump_tos] * len(self._elements)
        else:
            jump_to_list = self.jump_tos
        unwrapped_tuples = []
        for awg in awg_ch_dict:
            ch_list = awg_ch_dict[awg]
            unwrapped_tuples.append(
                (wf_dict[awg], m1_dict[awg], m2_dict[awg], nrep_list,
                    trig_wait_list, goto_state_list, jump_to_list, ch_list))
        return unwrapped_tuples

    def wrap(self, tup: Tuple[tuple, dict]):
        """
        Function which reconstructs a Sequence object from the tuple object
        returned by the parse_awg_file function of the AWGFileParser in the
        QCoDeS Tektronix AWG5014 driver.

        Args:
            -  tuple: (tuple, dict), where the first element of the tuple is \
          (wfms, m1s, m2s, nreps, trigs, gotos, jumps, channels) \
          and the second is a dict containing all instrument settings from the
          file.

        Returns:
            - Sequence object corresponding to the sequence in the file
        """
        (wf_lists, m1_lists, m2_lists, nrep_list,
         trig_wait_list, goto_state_list, jump_to_list, chan_list) = tup[0]

        elem_length = len(wf_lists[0])
        chan_length = len(chan_list)
        if any(len(lst) != elem_length for lst in [m1_lists[0], m2_lists[0],
                                                   nrep_list, trig_wait_list,
                                                   goto_state_list,
                                                   jump_to_list]):
            raise ValueError('Cannot form Sequence: not all from (wf_lists, '
                             'm1_lists, m2_lists, nrep_list, trig_wait_list, '
                             'goto_state_list, jump_to_list, chan_list) have '
                             'same length (corresponding to element number)')
        elif any(len(lst) != chan_length for lst in [wf_lists, m1_lists,
                                                     m2_lists]):
            raise ValueError('Not all from Cannot from  (chan_list, wf_lists, '
                             'm1_lists, m2_lists) provided for Sequence '
                             'building have same length (corresponding to '
                             'number of channels used)')

        self.clear()

        self.nreps = nrep_list
        self.trig_waits = trig_wait_list
        self.goto_states = goto_state_list
        self.jump_tos = jump_to_list

        for j in range(elem_length):
            element = Element()
            for i, chan in enumerate(chan_list):
                waveform = Waveform(channel=chan)
                waveform.wave = wf_lists[i][j]
                markers = Segment._raw_to_points({1: m1_lists[i][j],
                                                  2: m2_lists[i][j]})
                for i in [1, 2]:
                    for m in markers[i]:
                        waveform.add_marker(i, m['delay_points'],
                                            m['duration_points'])
                element.add_waveform(waveform)
            self.add_element(element)

        self.check()

    def check(self):
        """
        Function which checks the sequence, passing if:
        1) sequence has nonzero length
        2) if present variable array is the same length as sequence
        3) nreps, trig_waits, goto_states are ints or lists
           of the same length as the sequence
        4) each element passes element check
        5) all elements have the same number of waveforms in
        """
        if not self._elements:
            raise RuntimeError('no elements in sequence')
        self._test_variable_array_length()
        self._test_sequence_variables()
        for i, element in enumerate(self._elements):
            try:
                element.check()
            except Exception as e:
                raise Exception(
                    'error in element {}: {}'.format(i, e))
        self._test_element_waveform_count()
        print('sequence check passed: {} elements'.format(len(self)))
        return True

    def copy(self):
        return copy.deepcopy(self)

    def has_key(self, k):
        return k in self._elements

    def update(self, *args, **kwargs):
        return self._elements.update(*args, **kwargs)

    def pop(self, *args):
        return self._elements.pop(*args)

    def plot(self, elemnum: int=0, channels: List[int]=None):
        """
        Function which plots channels and markers

        Args:
            sequence to plot
            elemnum to plot (default 0)
            channels (default [1, 2]) to plot

        Returns:
            matplotlib fig
        """
        elem = self[elemnum]
        return elem.plot(channels=channels)

    def print_segment_lists(self, elemnum: int=0, channels: List[int]=[1, 2]):
        """
        Prints segment lists for specific element

        Args:

        """
        elem = self[elemnum]
        elem.print_segment_lists(channels=channels)

    def _test_variable_array_length(self):
        """
        Test which raises an exception if there is a variable array set
        that does not correspond to the length of the sequence
        """
        if (self.variable_array is not None and
                len(self.variable_array) != len(self)):
            raise Exception(
                'number of elements in sequence does not match length of '
                'variable_array defined by setting start, stop, step on '
                'initialisation. Variable array length {}, sequence '
                'length{}'.format(len(self.variable_array), len(self)))

    def _test_sequence_variables(self):
        """
        Test which checks the validity of nreps, trig_waits and goto_states
        for use with the unwrap function to generate a sequence
        """
        if all(isinstance(i, int) for i in
               [self.nreps, self.trig_waits, self.goto_states]):
            return
        elif not (isinstance(self.nreps, list) or
                  len(self.nreps) != len(self._elements)):
            raise Exception('nreps must be an int or a list of the same length'
                            ' as the sequence')
        elif not (isinstance(self.trig_waits, list) or
                  len(self.trig_waits) != len(self._elements)):
            raise Exception('trig_waits must be an int or a list of the same '
                            'length as the sequence')
        elif not (isinstance(self.goto_states, list) or
                  len(self.goto_states) != len(self._elements)):
            raise Exception('goto_states must be an int or a list of the same '
                            'length as the sequence')
        pass

    def _test_element_waveform_count(self):
        lengths = [len(element) for element in self._elements]
        # option1: all elements have same number of waveforms
        option1 = lengths.count(lengths[0]) == len(self._elements)
        # option2: first element has most waveforms and others have same number
        if len(self._elements) > 1:
            option2 = (all(i < lengths[0] for i in lengths[1:]) and
                       (lengths.count(lengths[1]) == (len(lengths) - 1)))
        else:
            option2 = False
        if not option1 or option2:
            raise Exception(
                'the elements of this sequence are '
                'not of lengths [l, l, ...] or lengths'
                ' [m, l, l, ...] where m > l : {}'.format(str(lengths)))
        if option2:
            raise NotImplementedError('awg upload doesn\'t support '
                                      '  [m, l, l, ...] where m > l format:'
                                      ' format given: {}'.format(str(lengths)))
