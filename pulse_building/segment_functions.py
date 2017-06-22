import numpy as np


def ramp(start, stop, dur, SR):
    points = round(SR * dur)
    return np.linspace(start, stop, points)


def gaussian(sigma, sigma_cutoff, amp, SR):
    points = round(SR * 2 * sigma_cutoff * sigma)
    t = np.linspace(-1 * sigma_cutoff * sigma, sigma_cutoff * sigma,
                    num=points)
    y = amp * np.exp(-(t**2 / (2 * sigma**2)))
    return y


def flat(amp, dur, SR):
    points = round(SR * dur)
    return amp * np.ones(points)


def gaussian_derivative(sigma, sigma_cutoff, amp, SR):
    points = round(SR * 2 * sigma_cutoff * sigma)
    t = np.linspace(-1 * sigma_cutoff * sigma, sigma_cutoff * sigma,
                    num=points)
    y = -amp * t / sigma * np.exp(-(t / (2 * sigma))**2)
    return y


def ramp_with_gaussian_rise():
    raise NotImplementedError


def sin_wave():
    raise NotImplementedError


def cos_wave():
    raise NotImplementedError


def sin_wave_gaussian_envelope():
    raise NotImplementedError


def cos_wave_gaussian_envolope():
    raise NotImplementedError
