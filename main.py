import glob
import os
from typing import List, Callable

import numpy as np
import scipy
import tqdm

from .myclass import GlobalConfig, Exdata
from .mylib import parse_data, seq_filter



########## Program Configure ##########
# Initialize Configure manually
# TODO: replace by YAML loader
conf = GlobalConfig(Path='./data', Workspace='./analysis_result')
num_unknown: int = 2000

# Make Workspace Directory
os.makedirs(conf.Workspace, exist_ok=True)


########## Preprocess ##########
# Create Data Struct
data_master = np.zeros(conf.n_Ch, num_unknown, conf.n_Trial, conf.n_Session)

n_subject: int = 3

ERP = {
    "t_ave": np.zeros(conf.n_Ch, n_subject),
    "f_ave": np.zeros(conf.n_Ch, n_subject),
    "e_ave": np.zeros(conf.n_Ch, n_subject),
}

BMI = {
    'I_ave': np.zeros(len(conf.COI), num_unknown, n_subject),
}

RandomBeep ={
    'ave': np.zeros(len(conf.COI), num_unknown, n_subject),
}

EMG = {
    'ave': np.zeros(len(conf.COI), num_unknown, n_subject)
}

# Load Data
for p in tqdm.tqdm(conf.Path):
    assert os.path.exists(p), f"FileNotFound: Check path, got {p}"
    if os.path.isfile(p):
        paths = [p]
    elif os.path.isdir(p):
        paths = glob.glob(f'{p}/**/*.mat') # TODO: Set the exact pattern of target
    
    data_raw = {
        os.path.basename(p).split('.')[0]: Exdata.from_mat_file(p)
        for p in paths 
    }

# Filter
filters = [
    lambda data: scipy.signal.detrend(data),
    lambda data: scipy.signal.filtfilt(
        *conf.Filter.Fstop[::-1],
        data
    ),
    lambda data: scipy.signal.filtfilt(
        *conf.Filter.Fpass[::-1],
        data
    )
]

data_filt = {
    k: seq_filter(v, filters)
    for k, v in data_raw.items()
} 