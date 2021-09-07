import glob
import os
from typing import List, Callable

import numpy as np
import scipy
import tqdm

from myclass import GlobalConfig, Exdata
from mylib import parse_data, seq_filter



########## Program Configure ##########
print('Set Program Config')
# Initialize Configure manually
# TODO: replace by YAML loader
conf = GlobalConfig(Path='./data_ST', Workspace='./analysis_result')
num_unknown: int = 2000

# Make Workspace Directory
os.makedirs(conf.Workspace, exist_ok=True)

print(f'Current Settings')
print(conf._asdict())
########## Preprocess ##########
# Create Data Struct
data_master = np.zeros((conf.n_Ch, num_unknown, conf.n_Trial, conf.n_Session))

n_subject: int = 3

ERP = {
    "t_ave": np.zeros((conf.n_Ch, n_subject)),
    "f_ave": np.zeros((conf.n_Ch, n_subject)),
    "e_ave": np.zeros((conf.n_Ch, n_subject)),
}

BMI = {
    'I_ave': np.zeros((len(conf.COI), num_unknown, n_subject)),
}

RandomBeep ={
    'ave': np.zeros((len(conf.COI), num_unknown, n_subject)),
}

EMG = {
    'ave': np.zeros((len(conf.COI), num_unknown, n_subject))
}

# Load Data
print(f'Start Data Loading @ {conf.Path}')
assert os.path.exists(conf.Path), f"FileNotFound: Check path, got {conf.Path}"
if os.path.isfile(conf.Path):
    print('path set as Filename')
    paths = [conf.Path]
elif os.path.isdir(conf.Path):
    print('path set as directory name')
    paths = glob.glob(f'{conf.Path}/*.mat') # TODO: Set the exact pattern of target
    print(f'got path list {paths}')

data_raw = {}
for p in tqdm.tqdm(paths):
#     with tqdm.tqdm(paths) as pbar:
#         pbar.set_postfix(f'filename={p}')
    data_raw = {
        os.path.basename(p).split('_')[1]: Exdata.from_mat_file(p)
        for p in paths
    }
print(f'Data Loaded\n    {data_raw}')

# Filter
print(f'Filter Process')
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
    k: seq_filter(v.EEG, filters)
    for k, v in tqdm.tqdm(data_raw.items())
} 
print(f'Filter Process DONE')