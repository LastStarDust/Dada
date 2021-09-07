import time
from collections import deque

import matplotlib.pyplot as plt

import dwf
from dada.discovery_manager import discovery_manager
from dada.threads import ResumableThread


class UartDebugger(ResumableThread):
    ACQ_RATE = 100000  # Hz
    VOLT_RANGE = 5  # V

    def __init__(self, resource_manager: dwf.DwfDevice, acquisition_window: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._in_chans = [0]
        self._num_samples = self.ACQ_RATE * acquisition_window
        self._buffer_length = 8000
        self._queue = {}

        device = resource_manager.open()
        self.dwf_ai = dwf.DwfAnalogIn(device)
        for channel in self._in_chans:
            self._queue[channel] = deque(maxlen=self._num_samples)
            self.dwf_ai.channelEnableSet(idxChannel=channel, enable=True)
            self.dwf_ai.channelRangeSet(idxChannel=channel, voltsRange=self.VOLT_RANGE)
            self.dwf_ai.acquisitionModeSet(acqmode=dwf.DwfAnalogIn.ACQMODE.SCAN_SHIFT)
            self.dwf_ai.frequencySet(hzFrequency=self.ACQ_RATE)
            self.dwf_ai.bufferSizeSet(size=self._buffer_length)
            if self.dwf_ai.bufferSizeGet() != self._buffer_length:
                raise ValueError(f"Warning : reached buffer length limit : {self._buffer_length}")

        # wait at least 2 seconds for the offset to stabilize
        time.sleep(2)

    def run(self) -> None:

        for channel in self._in_chans:
            print(f"Starting acquisition for channel {channel}")
            self.dwf_ai.configure(reconfigure=False, start=True)

        while True:
            for channel in self._in_chans:
                status = self.dwf_ai.status(read_data=True)
                if status in [dwf.Dwf.STATE.CONFIG, dwf.Dwf.STATE.PREFILL, dwf.Dwf.STATE.ARMED]:
                    # Acquisition not yet started.
                    continue

                # Read data
                num_valid_samples = self.dwf_ai.statusSamplesValid()
                samples = self.dwf_ai.statusData(idxChannel=channel, data_num=num_valid_samples)
                self._queue[channel].append(samples)
                with self.state:
                    if self.paused:
                        break

    def get_data(self):
        data = {}
        for channel in self._in_chans:
            data[channel] = list(self._queue[channel])
            self._queue[channel].clear()
        return data


def _uart_debug() -> None:
    rm: dwf.DwfDevice = discovery_manager()
    acq_window = int(input("Insert the acquisition window width in seconds :"))
    debugger = UartDebugger(resource_manager=rm, acquisition_window=acq_window)
    debugger.start()
    input("Press entern when you want to store the sample")
    debugger.pause()
    samples_y = debugger.get_data()
    for channel, sample_y in samples_y.items():
        print(f"Plotting channel {channel}")
        plt.plot(sample_y)
        plt.title = f"Channel {channel}"
        plt.show()


if __name__ == '__main__':
    try:
        _uart_debug()
    except RuntimeError as err:
        print(f"Program terminated with error : {err}")
