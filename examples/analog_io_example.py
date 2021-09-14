"""
Reimplemeted the "Analog IO Example" code found at the web page:
https://digilent.com/reference/test-and-measurement/guides/waveforms-using-waveforms-sdk
using the class API of the dwf package.

The code was only tested with a DIGILENT Analog Discovery 2, however it should work with similar hardware that has
at least one analog input and one analog output.
"""

import matplotlib.pyplot as plt

import dwf
from dada.discovery_manager import discovery_manager


# noinspection PyUnresolvedReferences
def run_example() -> None:
    rm: dwf.DwfDevice = discovery_manager()

    with rm as device:
        device: dwf.Dwf

        # enable wavegen channel 0, set the waveform to sine, set the frequency to 1 Hz, the amplitude to 2v and
        # start the wavegen
        out_chan = 0
        node = dwf.DwfAnalogOut.NODE.CARRIER
        dwf_ao = dwf.DwfAnalogOut(device)
        dwf_ao.nodeEnableSet(idxChannel=out_chan, node=node, enable=True)
        dwf_ao.nodeFunctionSet(idxChannel=out_chan, node=node, func=dwf.DwfAnalogOut.FUNC.SINE)
        dwf_ao.nodeFrequencySet(idxChannel=out_chan, node=node, hzFrequency=1)
        dwf_ao.nodeAmplitudeSet(idxChannel=out_chan, node=node, amplitude=2)
        dwf_ao.configure(idxChannel=out_chan, start=True)

        # enable scope channel 1, set the input range to 5v, set acquisition mode to record, set the sample frequency
        # to 100kHz and set the record length to 2 seconds
        in_chan = 0
        acq_rate_hz = 100000  # 100 kHz
        num_samples = 200000
        dwf_ai = dwf.DwfAnalogIn(device)
        dwf_ai.channelEnableSet(idxChannel=in_chan, enable=True)
        dwf_ai.channelRangeSet(idxChannel=in_chan, voltsRange=5)
        dwf_ai.acquisitionModeSet(acqmode=dwf.DwfAnalogIn.ACQMODE.RECORD)
        dwf_ai.frequencySet(hzFrequency=acq_rate_hz)
        dwf_ai.recordLengthSet(length=num_samples / acq_rate_hz)

        print("Starting oscilloscope")
        dwf_ai.configure(reconfigure=False, start=True)

        samples = 0
        raw_sample = []
        while samples < num_samples:
            status = dwf_ai.status(read_data=True)
            if samples == 0 and status in [dwf.Dwf.STATE.CONFIG, dwf.Dwf.STATE.PREFILL, dwf.Dwf.STATE.ARMED]:
                # Acquisition not yet started.
                continue

            # get the number of samples available, lost & corrupted
            available_samples, lost_samples, corrupted_samples = dwf_ai.statusRecord()
            samples += lost_samples

            # skip reading samples if there aren't any
            if available_samples == 0:
                continue

            # cap the available samples if the buffer would overflow from what's really available
            if samples + available_samples > num_samples:
                available_samples = num_samples - samples

            # Read channel 1's available samples into the buffer
            raw_sample += dwf_ai.statusData(idxChannel=in_chan, data_num=available_samples)
            samples += available_samples

        dwf_ao.reset(idxChannel=out_chan)
        plt.plot(raw_sample)
        plt.show()


if __name__ == '__main__':
    try:
        run_example()
    except RuntimeError as err:
        print(f"Program terminated with error : {err}")
