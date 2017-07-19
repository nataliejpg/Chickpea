import numpy as np


def ramp(start, stop, dur, SR):
    points = int(SR * dur)
    return np.linspace(start, stop, points)


def gaussian(sigma, sigma_cutoff, amp, SR):
    points = int(SR * 2 * sigma_cutoff * sigma)
    t = np.linspace(-1 * sigma_cutoff * sigma, sigma_cutoff * sigma,
                    num=points)
    return amp * np.exp(-(t**2 / (2 * sigma**2)))


def flat(amp, dur, SR):
    points = int(SR * dur)
    return amp * np.ones(points)


def gaussian_derivative(sigma, sigma_cutoff, amp, SR):
    points = int(SR * 2 * sigma_cutoff * sigma)
    t = np.linspace(-1 * sigma_cutoff * sigma, sigma_cutoff * sigma,
                    num=points)
    return -amp * t / sigma * np.exp(-(t / (2 * sigma))**2)
