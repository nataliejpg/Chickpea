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
        'Licence :: MIT Licence',
        'Programming Language :: Python :: 3.5'
    ],

    keywords='pulsebuilding signal arbitrary waveform generator',

    url='https://github.com/nataliejpg/Chickpea',

    python_requires='>=3',

)
