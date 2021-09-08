import matplotlib as mpl
import matplotlib.pyplot as plt

import dwf
from dada.discovery_manager import discovery_manager
from dada.uart_debugger import UartDebugger


def _uart_debug() -> None:
    rm: dwf.DwfDevice = discovery_manager()
    acq_window: float = float(input("Insert the acquisition window width in seconds : "))
    debugger = UartDebugger(resource_manager=rm, acquisition_window=acq_window)
    debugger.start()
    input("Press entern when you want to store the sample : ")
    debugger.stop()
    samples_x, samples_y = debugger.get_data()
    for channel in samples_y.keys():
        print(f"Plotting channel {channel}")
        plt.plot(samples_x[channel], samples_y[channel])
        plt.title(f"Channel {channel}")
        plt.xlabel("Time (s)")
        plt.ylabel("Voltage (V)")
        plt.show()


if __name__ == '__main__':
    try:
        mpl.use('Qt5Agg')
        _uart_debug()
    except RuntimeError as err:
        print(f"Program terminated with error : {err}")
