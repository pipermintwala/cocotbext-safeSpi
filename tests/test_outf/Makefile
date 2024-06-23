# SIM ?= verilator
# EXTRA_ARGS += -Wno-MULTIDRIVEN
# EXTRA_ARGS += --trace-fst --trace-structs

SIM ?= icarus

TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/../hdl/spi_slave_outf.v

outf:
	$(MAKE) sim MODULE=test_outf TOPLEVEL=spi_slave_outf

include $(shell cocotb-config --makefiles)/Makefile.sim