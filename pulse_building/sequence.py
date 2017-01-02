import numpy as np
import copy
from . import Element


class Sequence:
    def __init__(self, name=None, variable=None, variable_unit=None,
                 start=None, stop=None, step=None, nreps=1, trig_waits=0,
                 goto_states=0, jump_tos=1):
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
                trig_wait_list, goto_state_list, jump_to_list)

    def set_variable_array(self, start, stop, step):
        number = int((stop - start) / step + 1)
        self.variable_array = np.linspace(start, stop, num=number)

    def clear(self):
        self._elements.clear()

    def add_element(self, element):
        if not isinstance(element, Element):
            raise TypeError('cannot add element not of type Element')
        self._elements.append(element)

    def channels_used(self):
        chans = list(self._elements[0].keys())
        return chans

    def copy(self):
        return copy.copy(self)

    def has_key(self, k):
        return k in self._elements

    def update(self, *args, **kwargs):
        return self._elements.update(*args, **kwargs)

    def pop(self, *args):
        return self._elements.pop(*args)

    def check(self):
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

    def _test_sequence_variables(self):
        if all(isinstance(i, int) for i in
               [self.nreps, self.trig_waits, self.goto_states]):
            return
        if (isinstance(self.nreps, list) and
                len(self.nreps) != len(self._elements)):
            raise Exception('list specified for element repetition (nreps)'
                            ' not the same length as the sequence')
        elif (isinstance(self.trig_waits, list) and
                len(self.trig_waits) != len(self._elements)):
            raise Exception('list specified for trig_waits not '
                            'the same length as the length of the sequence')
        elif (isinstance(self.goto_states, list) and
                len(self.goto_states) != len(self._elements)):
            raise Exception('list specified for goto_states not '
                            'the same length as the length of the sequence')

    def _test_variable_array_length(self):
        if (self.variable_array is not None and
                len(self.variable_array) != len(self._elements)):
            raise Exception('number of elements in sequence does not match '
                            'length of "start, stop, step" variable_array')
        pass

    def _test_element_waveform_numbers(self):
        lengths = [len(element) for element in self._elements]
        # option1: all elements have same number of waveforms
        option1 = lengths.count(lengths[0]) == len(lengths)
        # option2: first element has most waveforms and others have same number
        option2 = (all(i < lengths[0] for i in lengths[1:]) and
                   (lengths.count(lengths[1]) == (len(lengths) - 1)))
        if not option1 or option2:
            raise Exception(
                'the elements of this sequence are '
                'not of lengths [l, l, ...] or lengths'
                ' [m, l, l, ...] where m > l : {}'.format(str(lengths)))
        if option2:
            raise NotImplementedError('awg upload doesn\'t support '
                                      '  [m, l, l, ...] where m > l format:'
                                      ' format given: {}'.format(str(lengths)))
