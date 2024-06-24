module spi_slave_inf (input wire cs,   // Chip select (active low)
                      input wire sclk, // Serial clock
                      input wire mosi, // Master Out Slave In
                      output reg miso,
                      input wire rst); //Master In Slave Out
    always @(cs) begin
        if (cs)begin
            miso <= 1'bz;
            
        end
    end
    // reg buff;
    always@(rst)begin
        if (rst)begin
            miso <= 1'bz;
        end
    end
    // always @(negedge sclk)begin
    //     if (!cs)begin
    //         buff <= mosi;
    
    //     end
    // end
    always @(*) begin
        if (!cs)begin
            miso <= mosi;
        end
        
    end
    initial begin
        $dumpfile("spi_inf.vcd");
        $dumpvars(0);
    end
endmodule
