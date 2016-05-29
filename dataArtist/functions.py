import numpy as np


def RMS(x, axis=None, dtype=None):
    '''calculate the Root-Mean-Square of a given number or np.array'''
    return np.sqrt(np.mean(x*x, axis=axis, dtype=dtype))
