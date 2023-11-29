module spi_test (
    input wire cs,            // Chip select (active low)
    input wire sclk,          // Serial clock
    input wire mosi,          // Master Out Slave In
    output wire miso		// Master In Slave Out
);
spi dut(
	.cs(cs),
	.sclk(sclk),
	.mosi(mosi),
	.miso(miso)
);
initial begin
	$dumpfile("spiTest.vcd");
	$dumpvars;
end

endmodule