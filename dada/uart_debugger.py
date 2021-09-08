import time
from collections import deque

import numpy as nm

import dwf
from dada.threads import ResumableThread, StoppableThread


class UartDebugger(ResumableThread, StoppableThread):
    ACQ_RATE = 100000  # Hz
    VOLT_RANGE = 5  # V
    PROBE_ATTENUATION = 10  # x10 probe
    BUFFER_LENGTH = 8192

    def __init__(self, resource_manager: dwf.DwfDevice, acquisition_window: float, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._acquisition_window = acquisition_window
        self._in_chans = [0, 1]
        self._num_samples = int(self.ACQ_RATE * self._acquisition_window)
        self._queue = {}

        self._device = resource_manager.open()
        self._dwf_ai = dwf.DwfAnalogIn(self._device)
        for channel in self._in_chans:
            self._queue[channel] = deque(maxlen=self._num_samples)
            self._dwf_ai.channelEnableSet(idxChannel=channel, enable=True)
            self._dwf_ai.channelRangeSet(idxChannel=channel, voltsRange=self.VOLT_RANGE)
            self._dwf_ai.channelAttenuationSet(idxChannel=channel, attenuation=self.PROBE_ATTENUATION)
            self._dwf_ai.acquisitionModeSet(acqmode=dwf.DwfAnalogIn.ACQMODE.SCAN_SCREEN)
            self._dwf_ai.frequencySet(hzFrequency=self.ACQ_RATE)
            self._dwf_ai.bufferSizeSet(size=self.BUFFER_LENGTH)
            if self._dwf_ai.bufferSizeGet() != self.BUFFER_LENGTH:
                raise ValueError("Warning : reached buffer length limit : "
                                 f"{self._dwf_ai.bufferSizeGet()} != {self.BUFFER_LENGTH}")

        # wait at least 2 seconds for the offset to stabilize
        time.sleep(2)

    def __del__(self):
        self._dwf_ai.close()
        self._device.close()

    def run(self) -> None:
        super(UartDebugger, self).run()

        self._dwf_ai.configure(reconfigure=False, start=True)

        idx = 1
        # iterations = 0
        # num_acquired_samples = 0

        while True:
            with self._pause_cond:
                while self._paused:
                    self._pause_cond.wait()
                if self.is_stopped():
                    return

                # iterations += 1

                # Read index
                idx_write = self._dwf_ai.statusIndexWrite()
                # Calculate how many new samples are in the buffer
                num_valid_samples = (idx_write - idx) % self.BUFFER_LENGTH

                status = self._dwf_ai.status(read_data=True)
                if status in [dwf.Dwf.STATE.CONFIG, dwf.Dwf.STATE.PREFILL, dwf.Dwf.STATE.ARMED]:
                    # Acquisition not yet started.
                    continue

                samples = {}
                if idx + num_valid_samples <= self.BUFFER_LENGTH:
                    for channel in self._in_chans:
                        samples[channel] = self._dwf_ai.statusData2(idxChannel=channel, idxData=idx,
                                                                    data_num=num_valid_samples)
                    # num_acquired_samples += num_valid_samples
                    # print(iterations, "idx: ", idx, ", idx_write: ", idx_write, ", valid samples: ",
                    #       num_valid_samples, ", acquired samples: ", num_acquired_samples)
                    idx = idx_write
                else:
                    # print("wrapping")
                    num_valid_samples1 = self.BUFFER_LENGTH - idx
                    for channel in self._in_chans:
                        samples[channel] = self._dwf_ai.statusData2(idxChannel=channel, idxData=idx,
                                                                    data_num=num_valid_samples1)
                    # num_acquired_samples += num_valid_samples1
                    # print(iterations, "idx: ", idx, ", idx_write: ", idx_write, ", valid samples: ",
                    #       num_valid_samples1, ", acquired samples: ", num_acquired_samples)
                    idx = 0
                    num_valid_samples2 = num_valid_samples - num_valid_samples1 + 1
                    for channel in self._in_chans:
                        samples[channel] += self._dwf_ai.statusData2(idxChannel=channel, idxData=idx,
                                                                     data_num=num_valid_samples2)
                    # num_acquired_samples += num_valid_samples2
                    # print(iterations, "idx: ", idx, ", idx_write: ", idx_write, ", valid samples: ",
                    #       num_valid_samples2, ", acquired samples: ", num_acquired_samples)
                    idx = idx_write

                for channel in self._in_chans:
                    self._queue[channel].extend(samples[channel])

    def get_data(self):
        data_x = {}
        data_y = {}
        for channel in self._in_chans:
            data_y[channel] = list(self._queue[channel])
            period = 1. / float(self.ACQ_RATE)
            data_x[channel] = list(nm.arange(0, len(data_y[channel]) * period, period))
            self._queue[channel].clear()
        return data_x, data_y
