from typing import Tuple, Optional

import dwf


def discovery_manager() -> dwf.DwfDevice:
    """
    List all available devices to the terminal and let the user choose one, preferably an Analog Discovery 2.
    :return: resource manager for a DIGILENT device supported by the WaveForms SDK
    """

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

    return rm
