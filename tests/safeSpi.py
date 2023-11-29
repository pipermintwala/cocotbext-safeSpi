import cocotb
from cocotb_bus.bus import Bus
from typing import Optional
from cocotb.triggers import Timer
from cocotb.triggers import Edge
from cocotb.triggers import Event
from cocotb.clock import BaseClock


from dataclasses import dataclass
import logging


class Frame:
    def __init__(self, data, isInframe=False, isResponse=False):
        self.data = data
        self.isInframe = isInframe
        self.isResponse = isResponse
        self.crcPoly = 0b1011
        self.width = 32
        if self.isInframe:
            self.crcInit = 0b111
            if self.isResponse:
                self.crcStart, self.crcEnd = 26, 3
            else:
                self.crcStart, self.crcEnd = 31, 5

        else:
            self.crcInit = 0b101
            self.crcStart, self.crcEnd = 31, 3

    def readBits(self, start, end, frame):
        """Reading bitvalues from a frame,
        bitpositions start from 0"""
        bits = frame >> end
        ones = (2 ** (start + 1 - end)) - 1
        return bits & ones

    def readBitsvalue(self, start, end):
        """Reading bitvalues from the frame class,
        bitpositions start from 0"""
        return self.readBits(start, end, self.data)

    def editFrame(self, newData, start, end, frame):
        """Creating/Editing frames,
        bitpostions start from 0.returns a copy of the edited frame"""
        length = self.width
        start = start + 1
        newData = newData << end  # ends at end=end
        ones = (2 ** (length - start) - 1) << start | 2**end - 1
        frame = frame & ones
        frame = newData | frame
        return frame

    def editFramevalue(self, newData, start, end):
        """edits the data value in the frame class"""
        frame = self.data
        self.data = self.editFrame(newData, start, end, frame)

    def crcCalc(self):
        """Calculate crc for the bits over the frame"""
        frame = self.data
        start = self.crcStart
        end = self.crcEnd
        poly = self.crcPoly
        data = self.readBits(start, end, frame)
        init = self.crcInit
        n = poly.bit_length() - 1
        l = start - end
        data = self.editFrame(init, l + n, l + 1, data)
        data = data << n
        first = data.bit_length()
        shift = first - poly.bit_length()
        crc = self.readBits(first, shift, data)
        while True:
            crc = crc ^ poly
            bitsadded = poly.bit_length() - crc.bit_length()
            try:
                bits = self.readBits(shift - 1, shift - bitsadded, data)
            except:
                break
            crc = crc << bitsadded
            crc = crc | bits
            shift = shift - bitsadded
        if shift != 0:
            crc = crc << shift
            crc = crc | self.readBits(shift - 1, 0, data)

        return crc

    def crcAdd(self):
        crc = self.crcCalc()
        start = self.crcEnd
        end = start - self.crcInit.bit_length()
        start = start - 1
        self.editFramevalue(crc, start, end)

    def crcCheck(self):
        crc = self.crcCalc()
        start = self.crcEnd - 1
        end = start - self.crcInit.bit_length() + 1
        crcGiven = self.readBitsvalue(start, end)
        if crc != crcGiven:
            print("\nCRC CHECKSUM ERROR\n")


class SpiBus(Bus):
    _signals = ["sclk", "mosi", "miso", "cs"]

    def __init__(self, entity=None, prefix=None, **kwargs):
        signals = self._signals
        super().__init__(entity, prefix, signals, optional_signals=[], **kwargs)

    @classmethod
    def from_entity(cls, entity, **kwargs):
        return cls(entity, **kwargs)

    @classmethod
    def from_prefix(cls, entity, prefix, **kwargs):
        return cls(entity, prefix, **kwargs)


class SpiFrameError(Exception):
    pass


class SpiFrameTimeout(Exception):
    pass


@dataclass
class SpiConfig:
    """cpha = 0 :out-of-frame
    cpha = 1 :in-frame"""

    frame_width: int = 32
    sclk_freq: Optional[float] = 25e6
    cpol: bool = False
    cpha: bool = False
    frame_spacing_ns: int = 1
    data_output_idle: int = 1
    ignore_rx_value: Optional[int] = None


class SpiMaster:
    def __init__(self, bus: SpiBus, config: SpiConfig) -> None:
        self.log = logging.getLogger(f"cocotb.{bus.sclk._path}")

        # spi signals
        self._sclk = bus.sclk
        self._mosi = bus.mosi
        self._miso = bus.miso
        self._cs = bus.cs

        # size of a transfer
        self._config = config

        self.queue_tx = []
        self.queue_rx = []

        self.sync = Event()

        self._idle = Event()
        self._idle.set()

        self._sclk.setimmediatevalue(int(self._config.cpol))
        self._mosi.setimmediatevalue(self._config.data_output_idle)
        self._cs.setimmediatevalue(1)

        self._SpiClock = _SpiClock(
            signal=self._sclk,
            period=(1 / self._config.sclk_freq),
            units="sec",
            start_high=self._config.cpha,
        )

        self._run_coroutine_obj = None
        self._restart()

    def _restart(self) -> None:
        if self._run_coroutine_obj is not None:
            self._run_coroutine_obj.kill()
        self._run_coroutine_obj = cocotb.start_soon(self._run())

    async def write(self, frame: Frame, addCrc=True):
        """Adds crc to the frame and writes it with wait"""
        await self.write_nowait(frame, addCrc)
        await self._idle.wait()

    async def write_nowait(self, frame: Frame, addCrc=True):
        if addCrc:
            frame.crcAdd()
        self.queue_tx.append(frame.data)
        self.sync.set()
        self._idle.clear()

    async def read(self):
        while self.empty_rx():
            self.sync.clear()
            await self.sync.wait()
        return self.read_nowait()

    def read_nowait(self):
        if self._config.cpha:
            reg = self.queue_rx.pop()
        else:
            try:
                reg = self.queue_rx.pop(-2)
            except Exception:
                print("Wait for next frame for response")
                return
        return reg

    def count_tx(self):
        return len(self.queue_tx)

    def empty_tx(self):
        return not self.queue_tx

    def count_rx(self):
        return len(self.queue_rx)

    def empty_rx(self):
        return not self.queue_rx

    def idle(self):
        return self.empty_tx() and self.empty_rx()

    def clear(self):
        self.queue_tx.clear()
        self.queue_rx.clear()

    async def wait(self):
        await self._idle.wait()

    def _recieve(self):
        pass

    async def _run(self):
        while True:
            while not self.queue_tx:
                self._sclk.value = int(self._config.cpol)
                self._idle.set()
                self.sync.clear()
                await self.sync.wait()

            tx_word = self.queue_tx.pop(0)
            self._mosi.value = 0
            rx_word = 0

            self.log.debug("Write byte 0x%02x", tx_word)
            # the timing diagrams are CPHA/CPOL convention come from
            # https://en.wikipedia.org/wiki/Serial_Peripheral_Interface
            # this is also compliant with Linux Kernel definiton of SPI
            # if CPHA=0, the first bit is typically clocked out on edge of chip select
            if not self._config.cpha:
                self._mosi.value = bool(tx_word & (1 << self._config.frame_width - 1))

            # set the chip select
            self._cs.value = 0
            await Timer(self._SpiClock.period, units="step")

            await self._SpiClock.start()

            if self._config.cpha:
                # if CPHA=1, the first edge is propagate, the second edge is sample
                for k in range(self._config.frame_width):
                    # the out changes on the leading edge of clock
                    await Edge(self._sclk)
                    self._mosi.value = bool(
                        tx_word & (1 << (self._config.frame_width - 1 - k))
                    )

                    # while the in captures on the trailing edge of the clock
                    await Edge(self._sclk)
                    rx_word |= bool(self._miso.value.integer) << (
                        self._config.frame_width - 1 - k
                    )
            else:
                # if CPHA=0, the first edge is sample, the second edge is propagate
                # we already clocked out one bit on edge of chip select, so we will clock out less bits
                for k in range(self._config.frame_width - 1):
                    await Edge(self._sclk)
                    rx_word |= bool(self._miso.value.integer) << (
                        self._config.frame_width - 1 - k
                    )

                    await Edge(self._sclk)
                    self._mosi.value = bool(
                        tx_word & (1 << (self._config.frame_width - 2 - k))
                    )

                # but we haven't sampled enough times, so we will wait for another edge to sample

                await Edge(self._sclk)
                rx_word |= bool(self._miso.value.integer)

            # set sclk back to idle state
            await self._SpiClock.stop()
            self._sclk.value = self._config.cpol

            # wait another sclk period before restoring the chip select and mosi to idle (not necessarily part of spec)
            await Timer(self._SpiClock.period, units="step")
            self._cs.value = 1
            self._mosi.value = int(self._config.data_output_idle)

            # wait some time before starting the next transaction
            await Timer(self._config.frame_spacing_ns, units="ns")

            # if the ignore_rx_value has been set, ignore all rx_word equal to the set value
            if rx_word != self._config.ignore_rx_value:
                self.queue_rx.append(rx_word)
            self.sync.set()


class _SpiClock(BaseClock):
    def __init__(self, signal, period, units="step", start_high=True):
        BaseClock.__init__(self, signal)
        self.period = cocotb.utils.get_sim_steps(period, units)
        self.half_period = cocotb.utils.get_sim_steps(period / 2.0, units)
        self.frequency = 1.0 / cocotb.utils.get_time_from_sim_steps(
            self.period, units="us"
        )

        self.signal = signal

        self.start_high = start_high

        self._idle = Event()
        self._sync = Event()
        self._start = Event()

        self._idle.set()

        self._run_coroutine_obj = None
        self._restart()

    def _restart(self):
        if self._run_coroutine_obj is not None:
            self._run_cr.kill()
        self._run_cr = cocotb.start_soon(self._run())

    async def stop(self):
        self.stop_no_wait()
        await self._idle.wait()

    def stop_no_wait(self):
        self._start.clear()
        self._sync.set()

    async def start(self):
        self.start_no_wait()

    def start_no_wait(self):
        self._start.set()
        self._sync.set()

    async def _run(self):
        t = Timer(self.half_period)
        if self.start_high:
            while True:
                while not self._start.is_set():
                    self._idle.set()
                    self._sync.clear()
                    await self._sync.wait()

                self._idle.clear()
                self.signal.value = 1
                await t
                if self._start.is_set():
                    self.signal.value = 0
                    await t
        else:
            while True:
                while not self._start.is_set():
                    self._idle.set()
                    self._sync.clear()
                    await self._sync.wait()

                self._idle.clear()
                self.signal.value = 0
                await t
                if self._start.is_set():
                    self.signal.value = 1
                    await t


def reverse_word(n, width):
    return int("{:0{width}b}".format(n, width=width)[::-1], 2)
