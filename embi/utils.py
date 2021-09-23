from typing import List, Callable

import numpy as np
import omegaconf
import pandas as pd
from scipy.signal import butter


def interpolate_filter_config(conf: omegaconf.DictConfig) -> omegaconf.DictConfig:
    Fs = conf.filter.Fs
    Wn = (
        conf.filter.Bandpass[0] / (Fs/2),
        conf.filter.Bandpass[1] / (Fs/2)
    )
    stopWn = (
        conf.filter.Notch[0] / (Fs/2),
        conf.filter.Notch[0] / (Fs/2)
    )
    Fpass = butter(
        conf.filter.butter_N, Wn, btype='bandpass'
    )
    Fstop = butter(
        conf.filter.butter_N, stopWn, btype='bandpass'
    )
    
    new_conf = conf.copy()
    new_conf.filter.update({
        'Wn': Wn,
        'Fpass': Fpass,
        'StopWn': stopWn,
        'Fstop': Fstop
    })
    return conf


def read_eyeclosed_memo(path: str, n_trial: int) -> pd.DataFrame:
    cont = {}
    
    with open(path, 'r') as f:
        file = f.readlines()
    for f in file:
        line = f.rstrip().split(',')
        value = np.asarray([int(i) - 1 for i in line[1:]])  # python index starts from 0
        cont[line[0]] = np.bincount(value, minlength=n_trial)
    return pd.DataFrame(cont, index=np.arange(1, n_trial+1))

def parse_data(path: str) -> np.ndarray:
    '''
    Parse mat data

    Parameters
    ----------
    path: str
        Path to target file
    
    Returns
    -------
    raw data: np.ndarray
        Parsed Data
    
    Note
    ----
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.loadmat.html#scipy.io.loadmat
    '''

    return np.zeros(10)

def seq_filter(
    data: np.ndarray,
    filters: List[Callable[[np.ndarray], np.ndarray]]
) -> np.ndarray:
    """
    Run filter program by sequence
    
    Parameters
    ----------
    data: np.ndarray
        Target data
    
    filters: List[Callable[np.ndarray], np.ndarray]
        List of filters.
        These files will treat data sequentially
    """
    temp = data
    for f in filters:
        temp = f(temp)
    return temp
