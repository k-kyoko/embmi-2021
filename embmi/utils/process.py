from glob import glob
from typing import Any, Callable, Dict, List

import numpy as np
import omegaconf

from embmi.types import Exdata


__all__ = [
    'interpolate_filter_config',
    'parse_exdata',
    'run_seq_proc',
    'search_files',
]


def search_files(
    path: str,
    file_pattern: str,
    ignore_pattern: str = '',
    ignore_files: List[str] = [],
    ) -> List[str]:

    recursive = True
    files = glob(f'{path}/**/{file_pattern}', recursive=recursive)
    ifiles = []

    if ignore_pattern != '':
        ifiles.extend(glob(f'{path}/**/{ignore_pattern}', recursive=recursive))

    if ignore_files != []:
        for f in ignore_files:
            ifiles.extend(glob(f'{path}/**/{f}', recursive=recursive))

    return sorted([f for f in files if f not in ifiles])


def interpolate_filter_config(conf: omegaconf.DictConfig) -> omegaconf.DictConfig:
    Fs = conf.filter.Fs
    Wn = (
        conf.filter.Bandpass[0] / (Fs/2),
        conf.filter.Bandpass[1] / (Fs/2)
    )
    stopWn = (
        conf.filter.Notch[0] / (Fs/2),
        conf.filter.Notch[1] / (Fs/2)
    )

    new_conf = conf.copy()

    new_conf.filter.update({
        'Wn': Wn,
        'StopWn': stopWn,
    })
    return new_conf


def parse_exdata(data: Dict[str, Any], param: Dict[str, Any], *, session:int = 1) -> Exdata:
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

    data = data

    sr = float(data['EEGSamplingRate'][0])
    _din = data['evt_255_DINs']
    din = []
    for i in range(_din.shape[1]):
        label = str(_din[0, i][0])
        value = float(_din[1, i][0])
        din.append((label, value))

    eeg = np.zeros(0)
    for k in data.keys():
        if ('mff' in k) and ('EMG' not in k):
            eeg = data[k]

    randt = param['randt'][:, session-1]
    return Exdata(session, eeg, din, sr, randt)


def run_seq_proc(
    data: np.ndarray,
    filters: List[Callable[[np.ndarray], np.ndarray]]
) -> np.ndarray:
    """
    Run Sequential Process by sequence

    Parameters
    ----------
    data: np.ndarray
        Target data
    
    process: List[Callable[np.ndarray], np.ndarray]
        List of functions.
        These process will treat data sequentially
    """
    temp = data
    for f in filters:
        temp = f(temp)
    return temp
