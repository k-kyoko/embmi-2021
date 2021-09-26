from dataclasses import dataclass, field
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


@dataclass
class ExperimentConfig:
    file_pattern: str
    param_pattern: str
    eye_pattern: str

    n_Ch: int
    n_Trial: int
    n_Session: int
    Ref_ch: Tuple[int, int]
    COI: List[int]

    ignore_pattern: str = ''
    ignore_files: List[str] = field(default_factory=list)



@dataclass
class ScriptConfig:
    input_dir: str
    output_dir: str
    test_run: bool

    experiment: ExperimentConfig
    filter: FilterConfig
