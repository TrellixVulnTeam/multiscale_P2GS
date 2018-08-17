"""Script for manipulating ultrasound data for the LINK project
Author: Michael Pinkert
Organization: Laboratory for Optical and Computation Instrumentation, University of Wisconsin-Madison

"""

import scipy.io as sio
from pathlib import Path
import numpy as np


def open_iq(path_iq: Path) -> np.ndarray:
    """Open a .mat that holds IQData from the Verasonics system

    Input:
    A pathlib Path to an .mat file holding an 'IQData' variable, which is an array of complex numbers

    Output:
    A numpy array of complex numbers
    """
    mat_iq = sio.loadmat(str(path_iq))
    array_iq = mat_iq['IQData']
    return array_iq


def iq_to_bmode(array_iq: np.ndarray) -> np.ndarray:
    """Convert complex IQ data into bmode through log10 transform"""
    env = np.abs(array_iq)
    bmode = np.log10(env)

    return bmode


def read_position_list():
    return


def create_z_stack():
    return


def stitch_z_stacks():
    return



