module spi(
    input wire cs,         // Chip select (active low)
    input wire sclk,        // Serial clock
    input wire mosi,       // Master Out Slave In
    output reg miso        //Master In Slave Out
);
always @(cs) begin
   if (cs)
      miso <= 1'bz;
end
always @(posedge sclk) begin
   miso <= mosi;
end

endmodule