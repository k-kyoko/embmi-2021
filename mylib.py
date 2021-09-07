import numpy as np

from typing import List, Callable


def parse_data(path: str) -> np.ndarray:
    '''
    Parse mat data

    Parameters
    ----------
    path: str
        Path to target file
    
    Returns
    -------
    raw data: np.ndarray
        Parsed Data
    
    Note
    ----
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.loadmat.html#scipy.io.loadmat
    '''

    return np.zeros(10)

def seq_filter(
    data: np.ndarray,
    filters: List[Callable[[np.ndarray], np.ndarray]]
) -> np.ndarray:
    """
    Run filter program by sequence
    
    Parameters
    ----------
    data: np.ndarray
        Target data
    
    filters: List[Callable[np.ndarray], np.ndarray]
        List of filters.
        These files will treat data sequentially
    """
    temp = data
    for f in filters:
        temp = f(temp)
    return temp