from dataclasses import dataclass
from typing import List, Tuple

# import numpy as np
# import numpy.typing as npt
from omegaconf import MISSING

__all__ = [
    'ScriptConfig'
]

@dataclass
class FilterConfig:
    __FloatTuple = Tuple[float, float]

    Fs: float
    Bandpass: __FloatTuple
    Notch: __FloatTuple
    butter_N: int

    Wn: __FloatTuple = MISSING
    StopWn: __FloatTuple = MISSING
    # Fpass: npt.NDArray[np.floating] = MISSING
    # Fstop: npt.NDArray[np.floating] = MISSING


@dataclass
class ExperimentConfig:
    n_Ch: int
    n_Trial: int
    n_Session: int
    Ref_ch: Tuple[int, int]
    COI: List[int]


@dataclass
class ScriptConfig:
    input_dir: str
    output_dir: str
    file_pattern: str
    ignore_pattern: str
    ignore_files: List[str]
    
    experiment: ExperimentConfig
    filter: FilterConfig
