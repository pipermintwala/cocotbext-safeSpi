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
        frame = Frame(i)
        await master.write(frame)
        response = await master.read()
        print(hex(i))
        if response:
            print(hex(response))
        await master.wait()
        await master.wait()
