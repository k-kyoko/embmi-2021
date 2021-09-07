from typing import NamedTuple, Tuple, List

import numpy as np
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
        Wn = Bandpass / (Fs/2)
        stopWn = Notch / (Fs/2)
        return cls(
            Bandpass = Bandpass,
            Wn = Wn,
            Fpass = butter(butter_N, Wn),
            Notch = Notch,
            StopWn = stopWn,
            Fstop = butter(butter_N, stopWn)
        )

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