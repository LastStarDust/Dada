"""
Reimplemeted the "Digital IO Example" code found at the web page:
https://digilent.com/reference/test-and-measurement/guides/waveforms-using-waveforms-sdk
using the class API of the dwf package.

The code was only tested with a DIGILENT Analog Discovery 2, however it should work with similar hardware that has
at least 16 digital input/output pins.
"""

import time

import dwf
from dada.discovery_manager import discovery_manager


def run_sample() -> None:

    rm: dwf.DwfDevice = discovery_manager()

    with rm as device:
        device: dwf.Dwf
        dwf_dio = dwf.DwfDigitalIO(device)
        dwf_dio.outputEnableSet(0x00FF)

        try:
            # start with 100000000
            pin_state: int = 0x80

            while True:
                # calculate new output value
                pin_state = pin_state * 2
                if pin_state > 0x80:
                    pin_state = 0x01

                # set value on enabled IO pins
                dwf_dio.outputSet(pin_state)
                # fetch digital IO information from the device
                dwf_dio.status()
                # read state of all pins, regardless of output enable
                dw_read: int = dwf_dio.inputStatus()
                # print(dw_read as bitfield (32 digits, removing 0b at the front)
                print("Digital IO Pins: ", bin(dw_read)[2:].zfill(16))
                time.sleep(0.5)

        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    try:
        run_sample()
    except RuntimeError as err:
        print(f"Program terminated with error : {err}")
