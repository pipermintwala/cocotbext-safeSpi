import cocotb
from cocotbext.safeSpi import SpiMaster, SpiConfig, Frame, SpiBus
from components import TB, ScoreBoard

testframes = [0x0F0F0F0A, 0x00000003, 0xFFFFFFF8, 0x0F0F0F0A, 0x0FF2C8FE]


@cocotb.test()
async def dut_test_inf(dut):
    tb = TB(dut)
    await tb.dut_reset()
    pass
