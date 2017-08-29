## Chickpea

An pulse building module to help with building pulses and sequences for arbitrary waveform generators.

### Motivation
--------------
Make it possible to abstract pulses into gates, procudures or similar.
 To be able ot make use of the sequencing mode of the AWG5014C with QCoDeS

### Description
---------------
The module makes it possible to compose Segments from functions which generate 
the points of part of a pulse based on the funtion parameters.
These can then be strung together to form a  Waveform and markers added.
Waveforms can be used simultaneously by putting  those which should be executed simultaneously
onto the channels of an Element. An Element acts as a dictionary of Waveforms. Elements
can be ordered and put into a Sequence which acts as a list of elements.

Check out the examples in the jupyter notebooks found in the `examples` folder.

### Requirements
---------------
Only works with Python 3


### The name
---------------
William named his 'broadbean' <https://github.com/QCoDeS/broadbean> and I prefer chickpea as a pulse.
