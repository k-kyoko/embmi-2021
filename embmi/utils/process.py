from typing import List, Callable

import numpy as np
import omegaconf
# from scipy.signal import butter


__all__ = [
    'interpolate_filter_config',
    'parse_data',
    'seq_filter',
]


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

    # Fpass = butter(
    #     conf.filter.butter_N, Wn, btype='bandpass'
    # )
    # Fstop = butter(
    #     conf.filter.butter_N, stopWn, btype='bandpass'
    # )
    
    new_conf = conf.copy()
    new_conf.filter.update({
        'Wn': Wn,
        'StopWn': stopWn,
        # 'Fpass': Fpass,
        # 'Fstop': Fstop
    })
    return new_conf



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
