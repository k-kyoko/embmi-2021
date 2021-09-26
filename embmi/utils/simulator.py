from typing import Any

import numpy as np
import numpy.typing as npt
import scipy.integrate as integrate

__all__ = [
    "SampleData"
]


class SampleData:
    def __init__(
        self,
        filename: str = 'day1_t1',
        *,
        time: int = 400000,
        n_type: int = 5,
        n_ring: int = 80
    ):
        mff = np.asarray([self.create_sample_spike(time)] * 129)
        emg = self.create_sample_spike(time, I=0.7, u0 = 1.0, v0=1.0)

        setattr(self, f'{filename}mff', mff)
        setattr(self, f'{filename}mffEMG', emg)
        self.Impedances_EMG_0 = self.create_sample_ohm()

        self.EEGSamplingRate = np.asarray([[1000.]])
        self.PNSSSamplingRate = np.asarray([[1000.]])

        self.evt_255_DINs = self.create_sample_din(time, n_type, n_ring)

    def create_sample_din(self, time:int, n_type:int, n_ring:int) -> npt.NDArray[Any]:
        din_0 = [f'DIN{i}' for i in range(n_type)] * (time // n_ring)
        din_0 = np.array([np.array(e) for e in din_0])
        din_1 = np.linspace(0, time, len(din_0)).tolist()
        din_1 = np.array([np.array(i) for i in din_1])
        din_2 = np.array([np.array(1.) for _ in din_1])
        din_3 = din_1.copy()
        din = np.array([din_0, din_1, din_2, din_3], dtype=object)

        return din

    def create_sample_ohm(self) -> npt.NDArray[np.floating]:
        return np.random.exponential(15, 130).astype(dtype=np.float32).reshape(130, -1)

    def create_sample_spike(self, time, *, I=0.5, u0 = 2.0, v0 = 2.0) -> npt.NDArray[np.floating]:
        def d_u(u, v):
            c = 10
            return c * (-v + u - pow(u,3)/3 + I)

        def d_v(u, v):
            a = 0.7
            b = 0.8
            return u - b * v + a

        def fitzhugh(state, t):
            u, v = state
            deltau = d_u(u,v)
            deltav = d_v(u,v)
            return deltau, deltav

        t = np.arange(0.0, time*0.01, 0.01)

        y0 = [u0, v0]
        y = integrate.odeint(fitzhugh, y0, t)
        u_vec = y[:,0] 
        v_vec = y[:,1]

        return u_vec


    """
    Note
    ----
## Original data structure
    - __header__
        - byte
    - __version__
        - str
    - __globals__
        - list
    - SeiTakeda_tr1_1_20210801_122757mff
        - npt.NDArray(129, 423953, dtype=np.float32)
        - {filename}mff
        - EEGのデータ, 129ch x TimeScale
        - detrendした上で, 上がり下がりがある, 上がる時は基本スパイク
    - SeiTakeda_tr1_1_20210801_122757mffEMG
        - npt.NDArray(1, 423953), dtype=np.float32
        - {filename}mffEMG
        - EEGに対応する筋電のデータ, 1ch x TimeScale
        - 上がって下がってるを繰り返す
    - EEGSamplingRate
        - npt.NDArray(1, 1, dtype=np.float64)
        - unique
        - EEGのTimeScaleの単位時間がこれの逆数
        - fourierの時に使用した係数
        - 1000
    - Impedances_EEG_0
        - npt.NDArray(130, 1, dtype=np.float64)
        - unique
        - ohmマークのやつの情報
        - 電極のインピーダンス(最初の情報)
        - 基本は30以下, 40までがほとんど
    - PNSSamplingRate
        - npt.NDArray(1, 1, dtype=np.float64) ... 1000.
        - unique
        - 筋電のTimeScaleの単位時間がこれの逆数(要調査)
        - fourierの時に使用した係数
        - 1000
    - evt_255_DINs
        - npt.NDArray(4, 78, dtppe=object)
            - [0] ... NDArray[NDArray[np.str_]], DIN内容
            - [1] ... NDArray[NDArray[np.float_]], 正し中身は1x1, 狭義短調増加
            - [2] ... NDArray[NDArray[np.float_]], 正し中身は1x1, 全て1.
            - [3] ... NDArray[NDArray[np.float_]], 正し中身は1x1, 狭義短調増加
        - unique
        - readyなどの情報が被験者にどのタイミングで示されたかを記録する
            - 全体で揃ってないのは開手の成功がDINとして記録されるから
        - 4 x n_DIN
    """
