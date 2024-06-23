# SIM ?= verilator
# EXTRA_ARGS += -Wno-MULTIDRIVEN
# EXTRA_ARGS += --trace-fst --trace-structs

SIM ?= icarus

TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/../hdl/spi_slave_inf.v

inf:
	$(MAKE) sim MODULE=test_inf TOPLEVEL=spi_slave_inf

include $(shell cocotb-config --makefiles)/Makefile.sim