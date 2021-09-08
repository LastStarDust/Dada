import time
from collections import deque
from typing import Optional, List, Dict, Tuple

import numpy as nm

import dwf
from dada.threads import ResumableThread, StoppableThread


class UartDebugger(ResumableThread, StoppableThread):
    _ACQ_RATE = 100000  # Hz
    _VOLT_RANGE = 5  # V
    _PROBE_ATTENUATION = 10  # x10 probe
    _BUFFER_LENGTH = 8192
    _ENABLED_CHANNELS = [0, 1]

    def __init__(self,
                 resource_manager: dwf.DwfDevice,
                 acquisition_window: float,
                 acquisition_rate: Optional[float] = None,
                 volt_range: Optional[float] = None,
                 probe_attenuation: Optional[float] = None,
                 enabled_channels: Optional[List[int]] = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._acquisition_window: float = acquisition_window
        self._acquisition_rate: float = acquisition_rate if acquisition_rate is not None else self._ACQ_RATE
        self._volt_range: float = volt_range if volt_range is not None else self._VOLT_RANGE
        self._probe_attenuation: float = probe_attenuation if probe_attenuation is not None else self._PROBE_ATTENUATION
        self._in_chans: List[int] = enabled_channels if enabled_channels is not None else self._ENABLED_CHANNELS
        self._num_samples: int = int(self._ACQ_RATE * self._acquisition_window)
        self._queue: Dict[int, deque] = {}

        self._device = resource_manager.open()
        self._dwf_ai = dwf.DwfAnalogIn(self._device)

        for channel in self._in_chans:
            self._queue[channel] = deque(maxlen=self._num_samples)
            self._dwf_ai.channelEnableSet(idxChannel=channel, enable=True)
            self._dwf_ai.channelRangeSet(idxChannel=channel, voltsRange=self._volt_range)
            self._dwf_ai.channelAttenuationSet(idxChannel=channel, attenuation=self._probe_attenuation)
            self._dwf_ai.acquisitionModeSet(acqmode=dwf.DwfAnalogIn.ACQMODE.SCAN_SCREEN)
            self._dwf_ai.frequencySet(hzFrequency=self._acquisition_rate)
            self._dwf_ai.bufferSizeSet(size=self._BUFFER_LENGTH)
            if self._dwf_ai.bufferSizeGet() != self._BUFFER_LENGTH:
                raise ValueError("Warning : reached buffer length limit : "
                                 f"{self._dwf_ai.bufferSizeGet()} != {self._BUFFER_LENGTH}")

        # wait at least 2 seconds for the offset to stabilize
        time.sleep(2)

    def __del__(self):
        self._dwf_ai.close()
        self._device.close()

    def run(self) -> None:
        super(UartDebugger, self).run()

        self._dwf_ai.configure(reconfigure=False, start=True)

        idx = 1

        while True:
            with self._pause_cond:
                while self._paused:
                    self._pause_cond.wait()
                if self.is_stopped():
                    return

                # Read index
                idx_write: int = self._dwf_ai.statusIndexWrite()
                # Calculate how many new samples are in the buffer
                num_valid_samples: int = (idx_write - idx) % self._BUFFER_LENGTH

                status: dwf.Dwf.STATE = self._dwf_ai.status(read_data=True)
                if status in [dwf.Dwf.STATE.CONFIG, dwf.Dwf.STATE.PREFILL, dwf.Dwf.STATE.ARMED]:
                    # Acquisition not yet started.
                    continue

                samples: Dict[int, Tuple[float]] = {}
                if idx + num_valid_samples <= self._BUFFER_LENGTH:
                    for channel in self._in_chans:
                        samples[channel] = self._dwf_ai.statusData2(idxChannel=channel, idxData=idx,
                                                                    data_num=num_valid_samples)
                    idx = idx_write
                else:
                    num_valid_samples1: int = self._BUFFER_LENGTH - idx
                    for channel in self._in_chans:
                        samples[channel] = self._dwf_ai.statusData2(idxChannel=channel, idxData=idx,
                                                                    data_num=num_valid_samples1)
                    idx = 0
                    num_valid_samples2: int = num_valid_samples - num_valid_samples1 + 1
                    for channel in self._in_chans:
                        samples[channel] += self._dwf_ai.statusData2(idxChannel=channel, idxData=idx,
                                                                     data_num=num_valid_samples2)
                    idx = idx_write

                for channel in self._in_chans:
                    self._queue[channel].extend(samples[channel])

    def get_data(self) -> Tuple[Dict[int, List[float]], Dict[int, List[float]]]:
        data_x: Dict[int, List[float]] = {}
        data_y: Dict[int, List[float]] = {}
        for channel in self._in_chans:
            data_y[channel] = list(self._queue[channel])
            period = 1. / float(self._acquisition_rate)
            data_x[channel] = list(nm.arange(0, len(data_y[channel]) * period, period))
            self._queue[channel].clear()
        return data_x, data_y
