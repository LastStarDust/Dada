import dwf
from dada.discovery_manager import discovery_manager
from dada.uart_logger import UartLogger
from dada.uart_plotter import UartPlotter
import matplotlib as mpl


def _uart_debug() -> None:
    rm: dwf.DwfDevice = discovery_manager()
    acq_window: float = float(input("Insert the acquisition window width in seconds : "))
    logger = UartLogger(resource_manager=rm, acquisition_window=acq_window)
    logger.start()
    input("Press entern when you want to store the sample : ")
    logger.stop()
    samples_y = logger.get_data_y()
    logger.clear_data()
    plotter = UartPlotter(samples=samples_y, sample_period=logger.sample_period)
    plotter.plot()


if __name__ == '__main__':
    try:
        mpl.use('Qt5Agg')
        _uart_debug()
    except RuntimeError as err:
        print(f"Program terminated with error : {err}")
