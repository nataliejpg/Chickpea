from setuptools import setup

setup(
    name='chickpea',
    version='0.1',

    install_requires=['numpy>=1.12.1',
                      'matplotlib>=2.0.1'],

    author='Natalie Pearson',
    author_email='npearson@phys.ethz.ch',

    description=("Package for generating waveform sequences for use "
                 "with an AWG5014C or similar."),

    license='MIT',

    packages=['chickpea'],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.5'
    ],

    keywords='Pulsebuilding signal processing arbitrary waveforms',

    url='https://github.com/nataliejpg/Chickpea'
)
