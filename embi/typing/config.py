from dataclasses import dataclass
from typing import List, Tuple

from omegaconf import MISSING

@dataclass
class FilterConfig:
    __FloatTuple = Tuple[float, float]

    Fs: float
    Bandpass: __FloatTuple
    Notch: __FloatTuple
    butter_N: int

    Wn: __FloatTuple = MISSING
    Fpass: __FloatTuple = MISSING
    StopWn: __FloatTuple = MISSING
    Fstop: __FloatTuple = MISSING


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
