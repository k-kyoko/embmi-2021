import os
import sys
from typing import Tuple, cast

import numpy as np
import omegaconf
import pandas as pd
import scipy.signal
import tqdm
from omegaconf import OmegaConf

import embmi.types as types
import embmi.utils  as utils
from embmi.utils import log

########## Parameters ##########
CONFIG_PATH = './config.yml'


########## Program Configure ##########
conf: omegaconf.DictConfig

with log.biginform('Set Program Config'):
    with log.inform('Load YAML Config File'):
        conf_schema = OmegaConf.structured(types.ScriptConfig)
        conf_raw = OmegaConf.load(CONFIG_PATH)
        conf = cast(omegaconf.DictConfig, OmegaConf.merge(conf_schema, conf_raw))

    with log.inform('Interpolate configuration'):
        conf = utils.interpolate_filter_config(conf)

    with log.inform(f'Create Output dir at {conf.output_dir}'):
        os.makedirs(conf.output_dir , exist_ok=True)

    with log.inform('Validate the content'):
        if not os.path.isdir(conf.input_dir):
            log.alert(f"DirectoryNotFound: Check path, got {conf.input_dir}")
            raise FileNotFoundError(f'{conf.input_dir} not matched')

    log.inform(f'Load finished', '> ')
    log.inform(f'Current Settings', '> ')
    log.indicate(OmegaConf.to_yaml(conf))

########## Data Loading ##########
with log.biginform(f'Data Loading'):
    path = {}
    data = {}
    target = {
        'file': utils.load_file,
        'param': utils.load_param,
        'eye': lambda path, test_run: utils.load_eye(path, conf.experiment.n_Trial),
     }
    with log.inform(f'Search Target Files from {conf.input_dir}'):
        for k in target.keys():
            pattern = getattr(conf.experiment, f'{k}_pattern')
            path[k] = utils.search_files(
                conf.input_dir,
                pattern,
                conf.experiment.ignore_pattern,
                conf.experiment.ignore_files
            )
            log.inform(f'got {k} list: pattern = {pattern}', prefix='> ')
            log.indicate('\n'.join(path[k]))


    with log.inform('Validate Searched Target files'):
        for k, v in path.items():
            if len(v) == 0:
                log.alert(f'FILE NOT DETECTED > {k}_pattern: {v}')
                log.alert(f'Note: Some of the ignore patterns and files are excluded.')
                log.alert(f'Check your config')
                if not conf.test_run:
                    raise FileNotFoundError(f'{k}_pattern not matched')

        if len(path['file']) != len(path['param']):
            log.alert(f"Got different number of paths")
            log.alert(f"data:{len(path['file'])}, params:{len(path['param'])}")
            if not conf.test_run:
                raise RuntimeError('matched number of file_pattern and param_pattern is not the same')

    with log.inform(f'Load Target files'):
        for k, f in target.items():
            with log.inform(f'Load {k}', prefix='> '):
                data[k] = [f(p, test_run=conf.test_run) for p in tqdm.tqdm(path[k])]
                log.inform(f'got {k} data(first data):', '> ')
                log.indicate(f'{str(data[k][0])[:100]}...')


########## Pre Process ##########
with log.biginform('Process Data'):
    with log.inform('Parse Separated Dictionary data to DataClass'):
        data['exdata'] = [
            utils.parse_exdata(file, param, session = s)
            for s, (file, param) in tqdm.tqdm(
                enumerate(zip(data['file'], data['param']), 1)
            )
        ]
        log.inform(f'EXData Loaded', '> ')
        log.indicate(f'{str(data["exdata"][0])[:100]}...')

    with log.inform('Cut off while no-signal'):
        data['cut'] = []
        for ex in data['exdata']:
            temp = pd.DataFrame(ex.EEG)
            idx = temp.sum(0)
            eeg_sum = temp.drop(idx[idx==0].index, axis=1)
            data['cut'].append(cast(pd.DataFrame, eeg_sum).values)


    with log.inform('Apply Filter'):
        # TODO: Check if the btype is actually bandpass.
        fpass = cast(Tuple, scipy.signal.butter(
            conf.filter.butter_N, conf.filter.Wn, btype='bandpass'
        ))
        fstop = cast(Tuple, scipy.signal.butter(
            conf.filter.butter_N, conf.filter.StopWn, btype='bandstop'
        ))

        filters = [
            lambda data: scipy.signal.detrend(data),
            lambda data: scipy.signal.filtfilt(
                fstop[0], fstop[1],
                data,
                axis = 1
            ),
            lambda data: scipy.signal.filtfilt(
                fpass[0], fpass[1],
                data,
                axis = 1
            )
        ]

        data['filterdata'] = [
            utils.run_seq_proc(d, filters) for d in tqdm.tqdm(data['cut'])
        ]

    with log.inform('Search trial info'):
        data['idx_trial'] = []
        for d in data['exdata']:
            temp = {}
            i_trial = 1
            for din, time in d.DIN:
                if din == 'DIN2':
                    i_trial += 1
                if din == 'DIN6':
                    t = int(time)
                    temp[f'trial{i_trial}'] = [t-1000, t+999]
            data['idx_trial'].append(
                pd.DataFrame(temp, index=['start', 'stop']).T
            )

    with log.inform('Remove eyeclosed data'):
        data['idx_trial_eye'] = []
        target = zip(data['idx_trial'], data['eye'])
        for s, (idx, eye) in tqdm.tqdm(enumerate(target, 1)):
            col = eye.loc[:, f'session{s}']
            eye = col[col.values == 1].index
            eye = [f'trial{x}' for x in eye if f'trial{x}' in idx.index]
            log.inform(f'Dropped Trial in session{s}')
            log.indicate(''.join(eye))
            d = idx.drop(eye, axis=0)
            data['idx_trial_eye'].append(d)

    with log.inform('Split Session data by trial & Add Session Type'):
        data['master'] = []
        target = zip(data['idx_trial_eye'], data['filterdata'], data['exdata'])

        for idx, d, ex in tqdm.tqdm(target):
            temp = {}
            for trial, timing in idx.iterrows():
                temp[trial] = (
                    ex.Randt[int(trial[5:])],
                    d[:, timing.start:timing.stop]
                )
            data['master'].append(temp)

        log.inform('Created master table', '> ')
        example = data['master'][0]
        exkey = list(example.keys())[0]
        log.indicate(
            '\n'.join([
                f'{exkey}:',
                f'{example[exkey]}'
            ])
        )

    with log.inform('Split Session data by trial and its type'):
        data['master_true'] = []
        data['master_fake'] = []
        data['master_emg'] = []

        for m in tqdm.tqdm(data['master']):
            m_true = {}
            m_fake = {}
            m_emg = {}
            for trial, (seed, val) in m.items():
                if seed % 3 == 0:
                    m_fake[trial] = val
                if seed % 3 == 1:
                    m_emg[trial] = val
                if seed % 3 == 2:
                    m_true[trial] = val

            data['master_true'].append(m_true)
            data['master_fake'].append(m_fake)
            data['master_emg'].append(m_emg)


sys.exit(0)

########## Parse data by conditions : randombeep / EMG / EEG : parse_data ##########

# ERP_EEG = dict : keys = str:n_session, values = np.ndarray:[129, time, trial]

########## Draw waveform of COI ##########
