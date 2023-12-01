# Interfacing safeSpi module using cocoTB

GitHub repository: https://github.com/pipermintwala/cocotbext-safeSpi

## Introduction

[SafeSPI](https://safespi.org/) V1.0 interface models for [cocotb](https://github.com/cocotb/cocotb).

Initial build, interface for the master's side

## Documentation
The classes `SpiConfig` and `SpiMaster` are largely based on schang412's [repo](https://github.com/schang412/cocotbext-spi).
To use these classes simply save the safeSpi.py in your tests folder and import them, example is in the tests folder.



### Frames
Each frame is 32-bit long and the `Frame` class is used to edit and/or add groups of bits (TA,data) to it.
The class can perform CRC calculations according to the SafeSpi specifications. Details regarding the frame's type (in or out-of, response or command) are necessary for accurate results.

To use safeSpi frames import the `Frame` class:

    from safeSpi import Frame

    frame = Frame(0x0F0F0F0A, isInframe=False, isResponse=True)

To calculate CRC over the bits for out-of-frame command frame (bits 31:3):

    crc = frame.crcCalc()

Or add the CRC to the frame automatically:

    frame.crcAdd()

Print the hex value of the frame:

    frame.print()

Perform CRC check on the frames data:

    frame.crcCheck()
This method prints out an error message and returns 0 in case of mismatch and returns 1 if the CRC matches



### SpiMaster
This class acts as the master of the SafeSpi slave. The important changes from [schang's](https://github.com/schang412) class are in the read and write methods to suit the specifications.

The read, read_nowait, write, and write_nowait commands now accept `Frame` instead of raw integers.
U can choose to check for CRC in the received frame or `addCrc` in the written frame.

    await master.read(crcCheck = True)
    await master.write(frame=frame, addCrc=True)
Whether the master reads according to in-frame or out-of-frame depends on the `SpiConfig` of the master.



### SpiConfig
The `cpha` parameter for the config decides if the read command returns the immediate frame that it received(in-frame) or the previous one(out-of-frame).
`cpha` = 1 is in-frame and = 0 for out-of-frame.

To configure the master as in-frame:

    frame safeSpi import SpiConfig, SpiMaster
    @cocotb.test()
    async def dut_test(dut):
        config = SpiConfig(cpha=1)
        bus = SpiBus.from_entity(dut)
        master = SpiMaster(bus,config)
  

