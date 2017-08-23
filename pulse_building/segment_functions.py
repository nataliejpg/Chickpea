import numpy as np


def ramp(start, stop, dur, SR):
    points = int(SR * dur)
    return np.linspace(start, stop, points)


def gaussian(sigma, sigma_cutoff, amp, SR):
    points = int(SR * 2 * sigma_cutoff * sigma)
    t = np.linspace(-1 * sigma_cutoff * sigma, sigma_cutoff * sigma,
                    num=points)
    return amp * np.exp(-(t**2 / (2 * sigma**2)))


def stairs(start, stop, step, dur, SR):
    step_num = int(round((stop - start) / step + 1))
    step_dur = dur / step_num
    step_points = int(round(SR * step_dur))
    step_values = np.linspace(start, stop, num=step_num)
    return np.hstack([np.ones(step_points) * val for val in step_values])


def flat(amp, dur, SR):
    points = int(SR * dur)
    return amp * np.ones(points)


def gaussian_derivative(sigma, sigma_cutoff, amp, SR):
    points = int(SR * 2 * sigma_cutoff * sigma)
    t = np.linspace(-1 * sigma_cutoff * sigma, sigma_cutoff * sigma,
                    num=points)
    return -amp * t / sigma * np.exp(-(t / (2 * sigma))**2)
