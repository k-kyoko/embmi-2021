import pickle
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from scipy.io import loadmat

__all__ = [
    'load_file',
    'load_param',
    'load_eye',
]


def load_file(path: str, *, test_run=False) -> Dict[str, Any]:
    
    if test_run:
        with open(path, 'rb') as f:
            temp = pickle.load(f).__dict__
    else:
        temp = loadmat(path)
    
    return temp


def load_param(path: str, *, test_run=False) -> List[str]:
    if not test_run:
        temp = loadmat(path)
    else:
        with open(path, 'rb') as f:
            temp = pickle.load(f)
    
    return temp



def load_eye(path: str, n_trial: int, *, test_run=False) -> pd.DataFrame:
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

