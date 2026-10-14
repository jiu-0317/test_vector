`timescale 1ns/10ps
// 벡터 기반 테스트벤치 (넷리스트 TOP_new.v / RTL 공용)
//  - stim.txt 한 줄 = i_clk 1사이클, "rstn ssn sclk mosi" 4문자
//  - 입력은 negedge 직후 인가, 출력은 다음 negedge 직전에 샘플
//  - expect 파일 한 줄: "<idx> <miso> <cmd_done>"   (미정(x/z)이면 'x' -> FPGA 비교에서 don't-care)
//  - +define+RTL 이면 RTL TOP, 아니면 게이트 넷리스트 TOP (VDD/VSS 포트 포함)
module tb_vec;
    parameter PERIOD = 100;                 // ns (기능 검증용, 실제 속도와 무관)
    reg  i_clk = 0, i_rstn = 0, i_ssn = 1, i_sclk = 0, i_mosi = 0;
    wire o_miso, o_cmd_done;

`ifdef RTL
    TOP dut (.i_clk(i_clk), .i_rstn(i_rstn), .i_ssn(i_ssn), .i_mosi(i_mosi),
             .i_sclk(i_sclk), .o_miso(o_miso), .o_cmd_done(o_cmd_done));
`else
    supply1 VDD; supply0 VSS;
    TOP dut (.i_clk(i_clk), .i_rstn(i_rstn), .i_ssn(i_ssn), .i_mosi(i_mosi),
             .i_sclk(i_sclk), .o_miso(o_miso), .o_cmd_done(o_cmd_done),
             .VDD(VDD), .VSS(VSS));
`endif

    integer fin, fout, ftrace, idx, r;
    reg [3:0] v;
    string stim_path, expect_path, trace_path;

    function [7:0] bitchar(input b);
        bitchar = (b === 1'b1) ? "1" : (b === 1'b0) ? "0" : "x";
    endfunction

    always #(PERIOD/2) i_clk = ~i_clk;

    initial begin
        if (!$value$plusargs("stim=%s", stim_path))     stim_path   = "stim.txt";
        if (!$value$plusargs("expect=%s", expect_path)) expect_path = "expect.txt";
        if (!$value$plusargs("trace=%s", trace_path))   trace_path  = "trace.txt";
        fin    = $fopen(stim_path, "r");
        fout   = $fopen(expect_path, "w");
        ftrace = $fopen(trace_path, "w");
        if (fin == 0) begin $display("cannot open %s", stim_path); $finish; end
`ifdef VCD
        $dumpfile("dump.vcd");
        $dumpvars(1, dut);          // TOP 스코프의 모든 넷 (토글 커버리지용)
`endif
        idx = 0;
        @(negedge i_clk);
        while (!$feof(fin)) begin
            r = $fscanf(fin, "%b\n", v);
            if (r == 1) begin
                #1;
                {i_rstn, i_ssn, i_sclk, i_mosi} = v;     // 벡터 인가 (negedge 직후)
                @(posedge i_clk);                        // 칩 클럭
                #(PERIOD/2 - 2);                         // 다음 negedge 직전 샘플
                $fwrite(fout, "%0d %s %s\n", idx, bitchar(o_miso), bitchar(o_cmd_done));
`ifdef RTL
                $fwrite(ftrace, "%0d in=%b miso=%b done=%b st=%0d acc_r=%02x\n", idx, v, o_miso,
                        o_cmd_done, dut.u_ctrl.state, dut.u_acc_r.o_data);
`else
                $fwrite(ftrace, "%0d in=%b miso=%b done=%b st=%0d acc_r=%02x cnt=%0d rdat=%04x\n", idx, v,
                        o_miso, o_cmd_done, dut.u_ctrl_state, dut.acc_r_data, dut.u_acc_acc_cnt, dut.u_spi_r_dat);
`endif
                idx = idx + 1;
            end
            @(negedge i_clk);
        end
        $display("done: %0d vectors -> %s", idx, expect_path);
        $fclose(fin); $fclose(fout); $fclose(ftrace);
        $finish;
    end
endmodule
