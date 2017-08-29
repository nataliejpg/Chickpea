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

### Installation

Should work with just 
```
$ git clone https://github.com/nataliejpg/Chickpea.git $CHICKPEA_INSTALL_DIR
$ cd $CHICKPEA_INSTALL_DIR
$ pip install .
```
which will install `numpy`, `matplotlib` dependencies if not found. If you are using a [virtual enviroment](https://github.com/pyenv/pyenv-virtualenv) then you are likely to come across 
`matplotlib` issues. `matplotlib` is not strictly necessary but if you do want to get it working
the easiest way is to use [(Ana)conda](https://conda.io/docs/index.html)
```
$ conda install matplotlib package=2.0.1
```

You can now fire up a python 3 interpreter and go
```
>>> import chickpea as pb
```

If you want to run the examples you will also need to install jupyter by `pip` or `conda`
```
$ pip install jupyter
```
or 
```
$ conda install jupyter
```

### The name
---------------
[William](https://github.com/WilliamHPNielsen) named his 'broadbean' <https://github.com/QCoDeS/broadbean> and I prefer chickpea as a pulse.
