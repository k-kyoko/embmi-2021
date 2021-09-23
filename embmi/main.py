import glob
import os
import sys
from typing import cast

import numpy as np
import omegaconf
import pandas as pd
import scipy
import tqdm
from omegaconf import OmegaConf

import embmi.types as types
import embmi.utils  as utils
from embmi.utils import log

########## Parameters ##########
CONFIG_PATH = './notebooks/config.yml'



########## Program Configure ##########
with log.biginform('Set Program Config'):
    with log.inform('Load YAML Config File'):
        conf_schema = OmegaConf.structured(types.ScriptConfig)
        conf_raw = OmegaConf.load(CONFIG_PATH)
        conf = OmegaConf.merge(conf_schema, conf_raw)

    with log.inform('Interpolate configuration'):
        conf = utils.interpolate_filter_config(cast(omegaconf.DictConfig, conf))

    with log.inform(f'Create Output dir at {conf.output_dir}'):
        os.makedirs(conf.output_dir , exist_ok=True)

    with log.inform('Validate the content'):
        assert os.path.isdir(conf.input_dir),\
            f"DirectoryNotFound: Check path, got {conf.input_dir}"

    log.inform(f'Load finished', '> ')
    log.inform(f'Current Settings', '> ')
    log.indicate(OmegaConf.to_yaml(conf))

########## Data Loading ##########
with log.biginform(f'Data Loading'):
    with log.inform(f'Search Target Files from {conf.input_dir}'):
        data_path = glob.glob(
            f'{conf.input_dir}/**/{conf.experiment.file_pattern}',
            recursive=True
        )

        log.inform(f'got path list: {data_path}', '> ')

        param_path = glob.glob(
            f'{conf.input_dir}/**/{conf.experiment.param_pattern}',
            recursive=True
        )
        log.inform(f'got params paths: {param_path}', '> ')

        eye_path = glob.glob(
            f'{conf.input_dir}/**/{conf.experiment.eye_pattern}',
            recursive=True
        )
        log.inform(f'got eye paths: {eye_path}', '> ')


    with log.inform('Validate Searched Target files'):
        if len(data_path) == 0:
            log.warn(f'NO EXPERIMENT DATA DETECTED > {data_path}')
        if len(param_path) == 0:
            log.warn(f'NO PARAMS DATA DETECTED > {param_path}')
        if len(eye_path) == 0:
            log.warn(f'NO EYECLOSED DATA DETECTED > {eye_path}')

        assert len(param_path) == len(data_path), \
            f"Got different number of paths, data:{len(data_path)}, params:{len(param_path)}"

    with log.inform('Load Eye Close data'):
        eye_data = [utils.read_eyeclosed_memo(e, conf.experiment.n_Trial) for e in eye_path]
        log.inform(f'got eye data(first data):', '> ')
        log.indicate(f'{eye_data[0]}...')

sys.exit(1)


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

########## Preprocess ##########
with log.biginform('Pre Process'):
    with log.inform('Create Data Struct'):
        num_unknown = 2000
        n_subject: int = 3

        data_master = np.zeros((
            conf.experiment.n_Ch,
            num_unknown,
            conf.experiment.n_Trial,
            conf.experiment.n_Session
        ))

        ERP = {
            "t_ave": np.zeros((conf.experiment.n_Ch, n_subject)),
            "f_ave": np.zeros((conf.experiment.n_Ch, n_subject)),
            "e_ave": np.zeros((conf.experiment.n_Ch, n_subject)),
        }
        BMI = {
            'I_ave': np.zeros((len(conf.experiment.COI), num_unknown, n_subject)),
        }
        RandomBeep ={
            'ave': np.zeros((len(conf.experiment.COI), num_unknown, n_subject)),
        }
        EMG = {
            'ave': np.zeros((len(conf.experiment.COI), num_unknown, n_subject))
        }


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
