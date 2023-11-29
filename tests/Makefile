SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/../hdl/spi.v
VERILOG_SOURCES += $(PWD)/wrappers/spi_test.v

dut:
	$(MAKE) sim MODULE=test TOPLEVEL=spi_test
include $(shell cocotb-config --makefiles)/Makefile.sim