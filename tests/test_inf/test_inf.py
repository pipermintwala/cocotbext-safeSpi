import cocotb
from cocotbext.safeSpi import SpiMaster, SpiConfig, Frame, SpiBus
from components import TB, ScoreBoard

testframes = [0x0F0F0F0A, 0x00000003, 0xFFFFFFF8, 0x0F0F0F0A, 0x0FF2C8FE]


@cocotb.test()
async def dut_test_inf_command(dut):
    testframes_command = [0x00000004, 0xFFFFFFF7, 0x0F0F0F13, 0x0FF2C8E7]
    tb = TB(dut)
    tb.spi_master.mode = 2  # inframe
    for i in testframes_command:
        frame = Frame(i, isInframe=True, isResponse=False)
        await tb.spi_master.write(frame)
        command = await tb.spi_master.read(isReponse=False)
        tb.scoreboard.output_callback(command)
        tb.scoreboard.output_expected_callback(frame)
    tb.scoreboard.check_scoreboard()
    await tb.dut_reset()


@cocotb.test()
async def dut_test_inf_response(dut):
    testframes_response = [0x00000006, 0xFFFFFFFC, 0x0F0F0F0A, 0x0FF2C8FE]
    tb = TB(dut)
    tb.spi_master.mode = 2  # inframe
    for i in testframes_response:
        frame = Frame(i, isInframe=True, isResponse=True)
        await tb.spi_master.write(frame)
        command = await tb.spi_master.read(isReponse=True)
        tb.scoreboard.output_callback(command)
        tb.scoreboard.output_expected_callback(frame)
    tb.scoreboard.check_scoreboard()
    await tb.dut_reset()
