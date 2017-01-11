import numpy as np
import copy
from . import Element

# TODO: test 'check' behaviour
# TODO: write tests
# TODO: make _test_sequence_variables test that variable values are valid
# TODO: decide whether to limit setattr behaviour, code at bottom


class Sequence:
    def __init__(self, name=None, variable=None, variable_unit=None,
                 start=None, stop=None, step=None, nreps=1, trig_waits=0,
                 goto_states=0, jump_tos=1):
        """
        Sequence class which represents a list of elements to run in order on
        an AWG with optional metadata information.
        ie one sequence has many elements

        Args:
            name (str): optional human readable identifier
            variable (str): optional name of the pyhsical variable varied
                            in each slemen of the sequence
            variable_unit (str): unit of the variable
            start (float): optional starting value of the variable
                           ie the value in elements[0]
            stop (float): optional finishing value of the variable
                          ie the value in elements[-1]
            step (float): optional step value of the variable
            nreps (int, array): number of times each element should be repeated
                                default 1
            trig_waits (int, array): trigger wait state for each element
                                     default 0
            goto_states (int, array): element to jump to after each element has
                                      finished (AWG indexing starts from 1)
                                      0 means jump to next, this is the default
            jump_tos (int, array): 'jump state' of each element (0: off, 1: on)
                                    default 1
        """

        self._elements = []
        self.nreps = nreps
        self.trig_waits = trig_waits
        self.goto_states = goto_states
        self.jump_tos = jump_tos
        self.name = name
        self.variable = variable
        self.variable_unit = variable_unit
        if all(not i for i in [start, stop, step]):
            self.variable_array = None
        elif all(isinstance(i, (float, int)) for i in [start, stop, step]):
            self.set_variable_array(start, stop, step)
        else:
            for i in [start, stop, step]:
                print(type(i))
            raise TypeError('start, stop and step must either all be '
                            'set as numbers (floats or ints) or none set')

    def __getitem__(self, key):
        return self._elements[key]

    def __setitem__(self, key, value):
        if not isinstance(value, Element):
            raise TypeError('element must be of type Element')
        self._elements[key] = value

    def __repr__(self):
        return repr(self._elements)

    def __len__(self):
        return len(self._elements)

    def __delitem__(self, key):
        del self._elements[key]

    def __cmp__(self, lst):
        return cmp(self._elements, lst)

    def __contains__(self, item):
        return item in self._elements

    def __iter__(self):
        return iter(self._elements)

    def unwrap(self):
        """
        Function which unwraps the sequence into a tuple of lists which
        are the inputs for the Tektronix_AWG5014 qcodes instument_driver
        make_send_and_load_awg_file function.

        Returns:
            - (waves, m1s, m2s, nreps, trig_waits,
               goto_states, jump_tos, channels)

               waves is of the form:
               [[wfm1ch1, wfm2ch1, ...], [wfm1ch2, wfm2ch2], ...]
               as are m1s and m2s

               channels is of the form [ch1, ch3]

               all others are arrays of the same length as the sequence
        """
        chan_list = self.channels_used()
        wf_lists = [[] for c in chan_list]
        m1_lists = [[] for c in chan_list]
        m2_lists = [[] for c in chan_list]
        for element in self._elements:
            for i, chan in enumerate(chan_list):
                wf_lists[i].append(element[chan].wave)
                m1_lists[i].append(element[chan].marker_1)
                m2_lists[i].append(element[chan].marker_2)
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
        return (wf_lists, m1_lists, m2_lists, nrep_list,
                trig_wait_list, goto_state_list, jump_to_list, chan_list)

    def set_variable_array(self, start, stop, step):
        """
        Function which sets the linear array of the variable being
        varied between sequence elements.

        Args:
            - start (float)
            - stop (float)
            - step (float)
        """
        number = int((stop - start) / step + 1)
        self.variable_array = np.linspace(start, stop, num=number)

    def clear(self):
        self._elements.clear()

    def add_element(self, element):
        """
        Function which adds an Element to the elements list
        """
        if not isinstance(element, Element):
            raise TypeError('cannot add element not of type Element')
        self._elements.append(element)

    def channels_used(self, element_index=0):
        """
        Function which calculates the channels used on an element

        Args:
            - element_index (int): default 0 (first element)

        Returns:
            - list of channels used
        """
        chans = list(self._elements[element_index].keys())
        return chans

    def check(self):
        """
        Function which checks the sequence, passing if:
        1) sequence has nonzero length
        2) if present variable array is the same length as sequence
        3) nreps, trig_waits, goto_states are ints or lists
           of the same length as the sequence
        4) all elements have the same number of waveforms in
        """
        if not self._elements:
            raise Exception('no elements in sequence')
        self._test_variable_array_length()
        self._test_sequence_variables()
        self._test_element_waveform_numbers()
        for i, element in enumerate(self._elements):
            try:
                element.check()
            except Exception as e:
                raise Exception(
                    'error in element {}: {}'.format(i, e))
        print('sequence check passed: {} elements'.format(len(self._elements)))
        return True

    def copy(self):
        return copy.copy(self)

    def has_key(self, k):
        return k in self._elements

    def update(self, *args, **kwargs):
        return self._elements.update(*args, **kwargs)

    def pop(self, *args):
        return self._elements.pop(*args)

    def _test_variable_array_length(self):
        """
        Test which raises an exception if there is a variable array set
        that does not correspond to the length of the sequence
        """
        if (self.variable_array is not None and
                len(self.variable_array) != len(self._elements)):
            raise Exception('number of elements in sequence does not match '
                            'length of "start, stop, step" variable_array')

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

    def _test_element_waveform_numbers(self):
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
