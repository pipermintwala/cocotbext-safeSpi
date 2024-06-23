module spi_slave_outf(cs,   // Chip select active low
                      sclk, // Serial clock
                      mosi, // Master Out Slave In
                      miso, //Master In Slave Out
                      rst);
    input cs;
    input sclk;
    input mosi;
    input rst;
    output miso;
    
    reg miso_reg;
    assign miso = miso_reg;
    
    reg [4:0] in_ptr;
    reg [31:0] in_buffer;
    reg [4:0] out_ptr;
    reg [31:0] out_buffer;
    reg have_response;
    
    
    always @(rst) begin
        if (rst)begin
            in_ptr        = 5'b0;
            out_ptr       = 5'b0;
            in_buffer     = 32'b0;
            out_buffer    = 32'b0;
            have_response = 0;
        end
    end
    
    always@(cs) begin
        if (cs)begin
            miso_reg <= 1'bz; //default
            in_ptr   <= 5'b0;
            out_ptr  <= 5'b0;
        end
    end
    
    //rx sequence
    always @(posedge sclk) begin
        if (in_ptr == 31) begin //full buffer
            in_buffer[in_ptr] = mosi; //store last val
            in_buffer     <= 32'b0;
            out_buffer    <= in_buffer; //store data
            have_response <= 1;//
        end
        else begin
            in_buffer[in_ptr] = mosi;
            in_ptr <= in_ptr+1;
        end
    end
    //tx sequence
    always @(negedge sclk or negedge cs) begin
        // $display("out_ptr:%d",out_ptr);
        if (have_response)begin
            miso_reg <= out_buffer[out_ptr];
            out_ptr  <= out_ptr+1;
        end
            if (out_ptr == 31) begin //empty buffer
                out_buffer    <= 32'b0;
                have_response <= 0;
            end
    end
    initial begin
        $dumpfile("spi_outf.vcd");
        $dumpvars(0);
    end
    
endmodule
