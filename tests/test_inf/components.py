from cocotb.log import SimLog
from cocotbext.safeSpi import SpiConfig, SpiBus, SpiMaster, Frame
from cocotb.triggers import Timer


class TB:
    def __init__(self, dut):
        self.dut = dut
        self.scoreboard = ScoreBoard()
        self.spi_config = SpiConfig(cpha=1)  # cpol stays zero
        self.spi_bus = SpiBus.from_entity(self.dut)
        self.spi_master = SpiMaster(self.spi_bus, self.spi_config)

    async def dut_reset(self):
        self.dut.rst.value = 1
        await Timer(200, "ns")
        self.dut.rst.value = 0
        await Timer(200, "ns")


class ScoreBoard:
    output = []
    output_expected = []

    def __init__(self) -> None:
        self.log = SimLog("ScoreBoard")
        self.errors = 0

    def output_callback(self, result: Frame):
        if result:
            if result.crcCheck():
                self.log.warning(f"CRC checksum error Frame:{result.hexVal()}\n")
                self.errors += 1
            self.output.append(result)

    def output_expected_callback(self, expected):
        self.output_expected.append(expected)

    def check_scoreboard(self):
        output_ls = self.output.copy()
        output_expected_ls = self.output_expected.copy()
        self.output.clear()
        self.output_expected.clear()

        if len(output_ls) != len(output_expected_ls):
            self.log.warning(
                f"Still expecting {len(output_expected_ls) - len(output_ls)} transactions on dut"
            )

            self.errors += 1

        else:
            for i, j in zip(output_ls, output_expected_ls):

                if i.checkEquality(j):
                    self.log.warning(
                        f"Expected and slave outputs don't match. Last mismatch: {i.hexVal()} != {j.hexVal()}"
                    )
                    self.errors += 1
                else:
                    self.log.warning(
                        f"Expected and slave outputs match. Last Pair: {i.hexVal()} = {j.hexVal()}"
                    )

        if self.errors:
            self.log.critical(
                f"Errors were recorded during the test,Total {self.errors} errors."
            )
            assert False
        self.log.warning(f"NO errors were recorded during the test.")
        assert True
