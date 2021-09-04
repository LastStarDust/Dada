# import sys
import time

# import dwfconstants as dwfc
import dwf


def run():
    #
    # hdwf = dwfc.c_int()
    # dw_read = dwfc.c_uint32()

    print("DWF Version: " + dwf.FDwfGetVersion())

    rm = dwf.DwfEnumeration()
    num_found_devices = len(rm)

    if num_found_devices <= 0:
        raise RuntimeError("No DIGILENT device found")

    print(f"Found {num_found_devices} devices")
    for device in rm:
        print(f'  index : "{device.idxDevice}", name : "{device.deviceName()}", user : "{device.userName()}"')

    device = None
    while device is None:
        if num_found_devices == 1:
            idx = rm[0].idxDevice
        else:
            idx = input("Please enter device index:\n")
        device = next((x for x in rm if x.idxDevice == idx), None)

    print(f"Opening device {device.deviceName()}")
    print(f'  index : "{device.idxDevice}"')
    print(f'  name : "{device.deviceName()}"')
    print(f'  user : "{device.userName()}"')
    print(f'  type : "{device.deviceType()[0].name}"')
    print(f'  revision : "{device.deviceType()[1].value}"')
    print(f'  serial number : "{device.SN()}"')
    print(f'  config : "{device.config()}"')

    # device.open()
    # device = dwf.DwfDevice(idxDevice=idx)
    # print(device.SN())


    #
    # if dwf_h.value == dwfc.hdwfNone.value:
    #     print("failed to open device")
    #     szerr = dwfc.create_string_buffer(512)
    #     dwf_h.FDwfGetLastErrorMsg(szerr)
    #     print(str(szerr.value))
    #     quit()
    #
    # dwf_h.FDwfDigitalIOOutputEnableSet(hdwf, dwfc.c_int(0x00FF))
    #
    # try:
    #     # start with 100000000
    #     pin_state = 0x80
    #
    #     while True:
    #         # calculate new output value
    #         pin_state = pin_state * 2
    #         if pin_state > 0x80:
    #             pin_state = 0x01
    #
    #         # set value on enabled IO pins
    #         dwf_h.FDwfDigitalIOOutputSet(hdwf, dwfc.c_int(pin_state))
    #         # fetch digital IO information from the device
    #         dwf_h.FDwfDigitalIOStatus(hdwf)
    #         # read state of all pins, regardless of output enable
    #         dwf_h.FDwfDigitalIOInputStatus(hdwf, dwfc.byref(dw_read))
    #
    #         # print(dw_read as bitfield (32 digits, removing 0b at the front)
    #         print("Digital IO Pins: ", bin(dw_read.value)[2:].zfill(16))
    #         time.sleep(0.5)
    #
    # except KeyboardInterrupt:
    #     # exit on ctrl+c
    #     pass
    # finally:
    #     # close opened connections
    #     dwf_h.FDwfDeviceClose(hdwf)


if __name__ == '__main__':
    run()
