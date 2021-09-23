import os

import numpy as np
import pandas as pd
from scipy.io import loadmat

from embmi.types import Exdata

__all__ = [
    'load_exdata',
    'read_eyeclosed_memo',
]


def load_exdata(path_data: str, path_params: str):
    data = loadmat(path_data)
    params = loadmat(path_params)

    session = int(os.path.basename(path_data).split('_')[1][1:2])
    params_num = int(os.path.basename(path_params).split('_')[1][-1])

    assert session == params_num, \
    f'Data number: {session} differs from params number: {params_num}'

    sr = float(data['EEGSamplingRate'][0])
    _din = data['evt_255_DINs']
    din = []
    for i in range(_din.shape[1]):
        label = str(_din[0, i][0])
        value = float(_din[1, i][0])
        din.append((label, value))

    eeg = None
    for k in data.keys():
        if ('mff' in k) and ('EMG' not in k):
            eeg = data[k]

    randt = params['randt'][:, params_num-1]
    return Exdata(session, eeg, din, sr, randt)


def read_eyeclosed_memo(path: str, n_trial: int) -> pd.DataFrame:
    cont = {}

    with open(path, 'r') as f:
        file = f.readlines()
    for f in file:
        line = f.rstrip().split(',')
        # python index starts from 0
        value = np.asarray([int(i) - 1 if i != '' else np.NaN for i in line[1:]])
        value = value[~np.isnan(value)].astype(np.int8)
        if len(value) != 0:
            cont[line[0]] = np.bincount(value, minlength=n_trial)
        else:
            cont[line[0]] = np.zeros(n_trial)
    return pd.DataFrame(cont, index=np.arange(1, n_trial+1))

