import multiprocessing
from collections import OrderedDict
from typing import Dict, List, Optional

import ripyl.protocol.uart as uart
import ripyl.streaming as stream
import ripyl.util.plot as rplot

CHANNEL_COLOR: Dict[int, str] = {0: 'orange', 1: 'blue'}
BITS: int = 8
PARITY: Optional[str] = None
STOP_BITS: int = 1


class UartPlotter(object):

    def __init__(self, samples: Dict[int, List[float]], sample_period: float):
        self._processes: List[multiprocessing.Process] = []
        self._samples: Dict[int, List[float]] = samples
        self._sample_period: float = sample_period

    def __enter__(self, *args, **kwargs):
        self.__init__(*args, **kwargs)
        return self

    @staticmethod
    def decoder_process(channel, data, period):
        print(f"Decoding channel : {channel}")

        txd = stream.samples_to_sample_stream(raw_samples=data, sample_period=period)
        records = list(uart.uart_decode(stream_data=txd, bits=BITS, parity=PARITY, stop_bits=STOP_BITS))
        success = True
        for rec in records:
            if rec.nested_status() != stream.StreamStatus.Ok:
                success = False
                print(f"Failed to decode record : {rec}")
                break
        if success:
            txd = stream.samples_to_sample_stream(raw_samples=data, sample_period=period)
            channels = OrderedDict([(f'CHANNEL {channel} : {CHANNEL_COLOR[channel]} (V)', txd)])
            title = "UART debug"
            plotter = rplot.Plotter()
            plotter.plot(channels=channels, annotations=records, title=title,
                         label_format=stream.AnnotationFormat.Text)
            plotter.show()

    def plot(self):
        for name, data in self._samples.items():
            self._processes.append(multiprocessing.Process(target=self.decoder_process,
                                                           args=(name, data, self._sample_period)))
            self._processes[-1].start()

    def __del__(self):
        for process in self._processes:
            process.join()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__del__()
