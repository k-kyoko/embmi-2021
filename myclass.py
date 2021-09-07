from glob import glob
import os
from typing import NamedTuple, Tuple, List
from pprint import pformat


import numpy as np
from scipy.io import loadmat
from scipy.signal import butter

FloatTuple = Tuple[float, float]

class FilterConfig(NamedTuple):
    """
    Filter Program Config
    
    Attributes
    ----------
    Bandpass: FloatTuple
    Wn: FloatTuple
    Fpass: FloatTuple
    Notch: FloatTuple
    StopWn: FloatTuple
    Fstop: FloatTuple
    butter_N: int
    """
    Bandpass: FloatTuple
    Wn: FloatTuple
    Fpass: FloatTuple
    Notch: FloatTuple
    StopWn: FloatTuple
    Fstop: FloatTuple
    butter_N: int

    @classmethod
    def generate(
        cls, 
        Fs: float, 
        Bandpass: FloatTuple,
        Notch: FloatTuple,
        butter_N: int = 3
    ):
        Wn = (Bandpass[0] / (Fs/2), Bandpass[1] / (Fs/2))
        stopWn = (Notch[0] / (Fs/2), Notch[1] / (Fs/2))
        return cls(
            Bandpass = Bandpass,
            Wn = Wn,
            Fpass = butter(butter_N, Wn, btype='bandpass'),
            Notch = Notch,
            StopWn = stopWn,
            Fstop = butter(butter_N, stopWn, btype='bandstop'),
            butter_N = butter_N
        )
    
    def __repr__(self) -> str:
        return pformat(self._asdict())

class GlobalConfig(NamedTuple):
    """
    Global Program Config

    Attributes
    ----------
    Path: List[str] ... You can set filename or directory path
    Workspace: str
    n_Ch: int = 129
    Fs: float = 1000
    n_Trial: int = 25  # Number of Trial in a Session
    n_Session: int = 6
    Ref_ch: Tuple[int, int] = (57, 100)
    COI: List[int] = [7, 31, 36, 55, 80, 104, 105, 106, 112, 129]; # sort ascending
    Filter: FilterConfig = FilterConfig.generate(Fs, [1, 20], [49, 51])
    """
    Path: List[str]
    Workspace: str
    n_Ch: int = 129
    Fs: float = 1000
    n_Trial: int = 25  # Number of Trial in a Session
    n_Session: int = 6
    Ref_ch: Tuple[int, int] = (57, 100)
    COI: List[int] = [7, 31, 36, 55, 80, 104, 105, 106, 112, 129]; # sort ascending
    # [6 13 112 7 106 30 105 31 80 37 87 55 54 79 129]
    Filter: FilterConfig = FilterConfig.generate(Fs, [1, 20], [49, 51])

    def __repr__(self) -> str:
        return pformat(self._asdict())

class Exdata(NamedTuple):
    """
    Data Structure for Experiment Data

    Attributes
    ----------
    trial: str
    EEG: np.ndarray
    DIN: List[tuple[str, float]]
    SamplingRate: float

    Class Methods
    -------------
    Exdata.from_mat_file(path: str)

    """
    trial: str
    EEG: np.ndarray
    DIN: List[Tuple[str, float]]
    SamplingRate: float

    def __repr__(self)->str:
        return f'Exdata(trial:{self.trial}, EEG:{self.EEG.shape}, DIN:({len(self.DIN)}), SamplingRate:{self.SamplingRate})'

    @classmethod
    def from_mat_file(cls, path: str):
        mat = loadmat(path)
        trial = os.path.basename(path).split('_')[1]
        sr = float(mat['EEGSamplingRate'][0])
        _din = mat['evt_255_DINs']
        din = []
        for i in range(_din.shape[1]):
            label = str(_din[0, i][0])
            value = float(_din[1, i][0])
            din.append((label, value))

        for k in mat.keys():
            if ('mff' in k) and ('EMG' not in k):
                eeg = mat[k]

        return cls(trial, eeg, din, sr)
