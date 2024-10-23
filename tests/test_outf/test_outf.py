from cocotb.triggers import Timer
import cocotb
from components import TB, Frame
import random


@cocotb.test()
async def dut_test_out_of_frame(dut):
    testframes = [0x00000003, 0xFFFFFFF8, 0x0F0F0F0A, 0x0FF2C8FE]  # out-frames
    tb = TB(dut)

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


@cocotb.test()
async def dut_test_out_of_frame_random(dut):
    tb = TB(dut)
    for i in range(100):
        frame = Frame(random.randint(0, 18446744073709551615))
        await tb.spi_master.write(frame=frame, addCrc=True)
        response = await tb.spi_master.read()
        tb.scoreboard.output_expected_callback(frame)
        tb.scoreboard.output_callback(response)
    await Timer(50, "ns")
    await tb.spi_master.write_zero()
    response = await tb.spi_master.read()
    tb.scoreboard.output_callback(response)
    tb.scoreboard.check_scoreboard()


@cocotb.test()
async def dut_test_out_of_frame_mismatch(dut):
    tb = TB(dut)
    frame = Frame(0x00000003)
    mismatch = Frame(0x00000002)
    await tb.spi_master.write(frame=frame)
    tb.scoreboard.output_expected_callback(frame)
    tb.scoreboard.output_callback(mismatch)
    await Timer(50, "ns")
    tb.scoreboard.check_scoreboard()


@cocotb.test()
async def dut_test_out_of_frame_crc_error(dut):
    tb = TB(dut)
    frame = Frame(0x0F0F0F0A)
    await tb.spi_master.write(frame=frame)
    response = await tb.spi_master.read()

    tb.scoreboard.output_expected_callback(frame)
    tb.scoreboard.output_callback(response)
    await tb.spi_master.write_zero()
    response = await tb.spi_master.read()
    tb.scoreboard.output_callback(response)
    await Timer(50, "ns")
    tb.scoreboard.check_scoreboard()
