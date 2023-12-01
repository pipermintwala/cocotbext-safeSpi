from cocotbext.safeSpi import Frame, SpiConfig, SpiBus, SpiMaster
from cocotb.triggers import Timer
import cocotb

testframes = [0x0F0F0F0A, 0x00000003, 0xFFFFFFF8, 0x0F0F0F0A, 0x0FF2C8FE]


@cocotb.test()
async def dut_test(dut):
    config = SpiConfig(cpha=1)
    bus = SpiBus.from_entity(dut)
    master = SpiMaster(bus, config)
    for i in testframes:
        frame = Frame(i, isInframe=False, isResponse=True)
        await master.write(frame=frame, addCrc=True)
        response = await master.read()
        print(hex(i))
        if response:
            response.print()
        await master.wait()
        await master.wait()
