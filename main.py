"""
Reimplemeted the "Digital IO Example" code found at the web page:
https://digilent.com/reference/test-and-measurement/guides/waveforms-using-waveforms-sdk
using the class API of the dwf package.

The code was only tested with a DIGILENT Analog Discovery 2, however it should work with similar hardware that has
at least 16 digital input/output pins.
"""

import time
from typing import Tuple, Optional

import dwf


def run_sample() -> None:
    print("DWF Version: " + dwf.FDwfGetVersion())

    device_enum: Tuple[dwf.DwfDevice] = dwf.DwfEnumeration()
    num_found_devices: int = len(device_enum)

    if num_found_devices <= 0:
        raise RuntimeError("No DIGILENT device found")

    print(f"Found {num_found_devices} devices")
    for rm in device_enum:
        print(f'  index : "{rm.idxDevice}", name : "{rm.deviceName()}", user : "{rm.userName()}"')

    rm: Optional[dwf.DwfDevice] = None
    while rm is None:
        if num_found_devices == 1:
            idx = device_enum[0].idxDevice
        else:
            idx = input("Please enter device index:\n")
        rm = next((x for x in device_enum if x.idxDevice == idx), None)

    device_type: dwf.DwfDevice.DEVID = rm.deviceType()[0]

    print(f'Opening device "{rm.deviceName()}"')
    print(f'  index : "{rm.idxDevice}"')
    print(f'  name : "{rm.deviceName()}"')
    print(f'  user : "{rm.userName()}"')
    print(f'  type : "{device_type.name}"')
    print(f'  revision : "{rm.deviceType()[1].value}"')
    print(f'  serial number : "{rm.SN()}"')
    print('----------------------------------')

    if rm.deviceType()[0] != rm.DEVID.DISCOVERY2:
        print(f'WARNING! Device type "{device_type.name}" is not tested')

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
