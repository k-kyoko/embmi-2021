from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import numpy.typing as npt

__all__ = [
    'Exdata',
]

@dataclass(frozen=True)
class Exdata:
    session: int
    EEG: npt.NDArray[np.floating]
    DIN: List[Tuple[str, float]]
    SamplingRate: float
    Randt: npt.NDArray[np.floating]
