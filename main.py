import glob
import os
from typing import List, Callable
from pprint import pformat

import numpy as np
import scipy
import pandas as pd
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
assert os.path.isdir(conf.Path), f"FileNotFound: Check path, got {conf.Path}"

paths = glob.glob(f'{conf.Path}/*.mat') # TODO: Set the exact pattern of target
print(f'got path list \n{pformat(paths)}')

paths_params = sorted(glob.glob(f'{conf.Path}/*params.mat'))
paths_data = sorted([i for i in paths if i not in paths_params])
print(f'got data paths: \n{pformat(paths_data)}, \nparams paths: {pformat(paths_params)}')
assert len(paths_params) == len(paths_data), \
f"Got different number of paths, data:{len(paths_data)}, params:{len(paths_params)}"

data_raw = {
    os.path.basename(pd).split('_')[1]: Exdata.from_mat_file(pd, pp)
    for (pd, pp) in tqdm.tqdm(zip(paths_data, paths_params))
}
print(f'Data Loaded\n{pformat(data_raw)}')

# Filter
print('Filter Process')
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
print('Filter Process DONE')


########## Split data by trials : TODO ##########

# data_trials = key=n_session, value=np.ndarray(129, time_length, n_trial(25))

########## Removing artifacted trials : TODO ##########

path_remove = sorted(glob.glob('./data_ST/removefiles_*'))
removefiles = []

for p in path_remove:
    temp = pd.read_csv(p, header=None).values
    removefiles.append(temp)
    
data_unart = data_filt

#for session in range(6):
#    for trial in n_trial:
#        if removefiles[session][0, trial] == exist ? 
#    data_unart[f'S{session}'][trial] = None


########## Parse data by conditions : randombeep / EMG / EEG : parse_data ##########

# ERP_EEG = dict : keys = str:n_session, values = np.ndarray:[129, time, trial]

########## Draw waveform of COI ##########
