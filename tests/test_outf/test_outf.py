from cocotb.triggers import Timer
import cocotb
from components import TB, Frame


# OUT_OF__FRAME TEST
@cocotb.test()
async def dut_test_out_of_frame(dut):
    testframes = [0x00000003, 0xFFFFFFF8, 0x0F0F0F0A, 0x0FF2C8FE]  # out-frames
    tb = TB(dut)

    await tb.dut_reset()

    for i in testframes:
        frame = Frame(i, isInframe=False, isResponse=True)
        await tb.spi_master.write(frame=frame)
        response = await tb.spi_master.read()
        tb.scoreboard.output_expected_callback(frame)
        tb.scoreboard.output_callback(response)
        await Timer(50, "ns")
    await tb.spi_master.write_zero()
    response = await tb.spi_master.read()
    tb.scoreboard.output_callback(response)

    tb.scoreboard.check_scoreboard()
