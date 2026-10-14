// Verilog for library ./lib/mychips_scl_0.0.1_tt_5.50v created by Liberate dev on Mon May 25 23:05:02 2026 for SDF version 2.1

// type:  
`timescale 1ns/10ps
`celldefine
module AND2X1 (Y, A, B, VDD, VSS);
	output Y;
	input A, B;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, int_fwire_Y, VDD__bar;

	and (int_fwire_Y, A, B);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module AND2X2 (Y, A, B, VDD, VSS);
	output Y;
	input A, B;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, int_fwire_Y, VDD__bar;

	and (int_fwire_Y, A, B);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module AOI21X1 (Y, A, B, C, VDD, VSS);
	output Y;
	input A, B, C;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, A__bar, B__bar;
	wire C__bar, int_fwire_0, int_fwire_1;
	wire int_fwire_Y, VDD__bar;

	not (C__bar, C);
	not (B__bar, B);
	and (int_fwire_0, B__bar, C__bar);
	not (A__bar, A);
	and (int_fwire_1, A__bar, C__bar);
	or (int_fwire_Y, int_fwire_1, int_fwire_0);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module AOI22X1 (Y, A, B, C, D, VDD, VSS);
	output Y;
	input A, B, C, D;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, A__bar, B__bar;
	wire C__bar, D__bar, int_fwire_0;
	wire int_fwire_1, int_fwire_2, int_fwire_3;
	wire int_fwire_Y, VDD__bar;

	not (D__bar, D);
	not (B__bar, B);
	and (int_fwire_0, B__bar, D__bar);
	not (C__bar, C);
	and (int_fwire_1, B__bar, C__bar);
	not (A__bar, A);
	and (int_fwire_2, A__bar, D__bar);
	and (int_fwire_3, A__bar, C__bar);
	or (int_fwire_Y, int_fwire_3, int_fwire_2, int_fwire_1, int_fwire_0);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module BUFX2 (Y, A, VDD, VSS);
	output Y;
	input A;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, int_fwire_Y, VDD__bar;

	buf (int_fwire_Y, A);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module BUFX4 (Y, A, VDD, VSS);
	output Y;
	input A;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, int_fwire_Y, VDD__bar;

	buf (int_fwire_Y, A);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module CLKBUFX1 (Y, A, VDD, VSS);
	output Y;
	input A;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, int_fwire_Y, VDD__bar;

	buf (int_fwire_Y, A);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module CLKBUFX2 (Y, A, VDD, VSS);
	output Y;
	input A;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, int_fwire_Y, VDD__bar;

	buf (int_fwire_Y, A);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module CLKBUFX4 (Y, A, VDD, VSS);
	output Y;
	input A;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, int_fwire_Y, VDD__bar;

	buf (int_fwire_Y, A);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module DFFNEGX1 (Q, D, CLK, VDD, VSS);
	output Q;
	input D, CLK;
	reg notifier = 1'b0;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Q, int_fwire_clk, int_fwire_IQ;
	wire int_fwire_Q, VDD__bar, xcr_0;

	not (int_fwire_clk, CLK);
	altos_dff_err (xcr_0, int_fwire_clk, D);
	altos_dff (int_fwire_IQ, notifier, int_fwire_clk, D, xcr_0);
	buf (int_fwire_Q, int_fwire_IQ);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Q, VDD__bar, VSS);
	altos_power_down (Q, int_fwire_Q, __PWD_DWN_OUT__Q);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module DFFPOSX1 (Q, D, CLK, VDD, VSS);
	output Q;
	input D, CLK;
	reg notifier = 1'b0;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Q, int_fwire_IQ, int_fwire_Q;
	wire VDD__bar, xcr_0;

	altos_dff_err (xcr_0, CLK, D);
	altos_dff (int_fwire_IQ, notifier, CLK, D, xcr_0);
	buf (int_fwire_Q, int_fwire_IQ);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Q, VDD__bar, VSS);
	altos_power_down (Q, int_fwire_Q, __PWD_DWN_OUT__Q);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module DFFSRX1 (Q, D, R, S, CLK, VDD, VSS);
	output Q;
	input D, R, S, CLK;
	reg notifier = 1'b0;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Q, int_fwire_IQ, int_fwire_Q;
	wire int_fwire_r, int_fwire_s, VDD__bar;
	wire xcr_0;

	not (int_fwire_s, S);
	not (int_fwire_r, R);
	altos_dff_sr_err (xcr_0, CLK, D, int_fwire_s, int_fwire_r);
	altos_dff_sr_0 (int_fwire_IQ, notifier, CLK, D, int_fwire_s, int_fwire_r, xcr_0);
	buf (int_fwire_Q, int_fwire_IQ);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Q, VDD__bar, VSS);
	altos_power_down (Q, int_fwire_Q, __PWD_DWN_OUT__Q);

	// Timing

	// Additional timing wires
	wire adacond0, adacond1, adacond2;
	wire adacond3, adacond4, adacond5;
	wire adacond6, adacond7, adacond8;
	wire CLK__bar, D__bar;


	// Additional timing gates
	and (adacond0, R, S);
	and (adacond1, D, S);
	and (adacond2, CLK, S);
	not (CLK__bar, CLK);
	and (adacond3, CLK__bar, S);
	not (D__bar, D);
	and (adacond4, D__bar, R);
	and (adacond5, CLK, R);
	and (adacond6, CLK__bar, R);
	and (adacond7, D, R, S);
	and (adacond8, D__bar, R, S);
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module FAX1 (CO, S, A, B, CI, VDD, VSS);
	output CO, S;
	input A, B, CI;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__CO, __PWD_DWN_OUT__S, A__bar;
	wire B__bar, CI__bar, int_fwire_0;
	wire int_fwire_1, int_fwire_2, int_fwire_3;
	wire int_fwire_4, int_fwire_5, int_fwire_6;
	wire int_fwire_CO, int_fwire_S, VDD__bar;

	and (int_fwire_0, B, CI);
	and (int_fwire_1, A, CI);
	and (int_fwire_2, A, B);
	or (int_fwire_CO, int_fwire_2, int_fwire_1, int_fwire_0);
	not (B__bar, B);
	not (A__bar, A);
	and (int_fwire_3, A__bar, B__bar, CI);
	not (CI__bar, CI);
	and (int_fwire_4, A__bar, B, CI__bar);
	and (int_fwire_5, A, B__bar, CI__bar);
	and (int_fwire_6, A, B, CI);
	or (int_fwire_S, int_fwire_6, int_fwire_5, int_fwire_4, int_fwire_3);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__CO, VDD__bar, VSS);
	altos_power_down (CO, int_fwire_CO, __PWD_DWN_OUT__CO);
	or (__PWD_DWN_OUT__S, VDD__bar, VSS);
	altos_power_down (S, int_fwire_S, __PWD_DWN_OUT__S);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module HAX1 (CO, S, A, B, VDD, VSS);
	output CO, S;
	input A, B;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__CO, __PWD_DWN_OUT__S, A__bar;
	wire B__bar, int_fwire_0, int_fwire_1;
	wire int_fwire_CO, int_fwire_S, VDD__bar;

	and (int_fwire_CO, A, B);
	not (A__bar, A);
	and (int_fwire_0, A__bar, B);
	not (B__bar, B);
	and (int_fwire_1, A, B__bar);
	or (int_fwire_S, int_fwire_1, int_fwire_0);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__CO, VDD__bar, VSS);
	altos_power_down (CO, int_fwire_CO, __PWD_DWN_OUT__CO);
	or (__PWD_DWN_OUT__S, VDD__bar, VSS);
	altos_power_down (S, int_fwire_S, __PWD_DWN_OUT__S);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module INVX1 (Y, A, VDD, VSS);
	output Y;
	input A;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, int_fwire_Y, VDD__bar;

	not (int_fwire_Y, A);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module INVX2 (Y, A, VDD, VSS);
	output Y;
	input A;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, int_fwire_Y, VDD__bar;

	not (int_fwire_Y, A);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module INVX4 (Y, A, VDD, VSS);
	output Y;
	input A;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, int_fwire_Y, VDD__bar;

	not (int_fwire_Y, A);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module INVX8 (Y, A, VDD, VSS);
	output Y;
	input A;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, int_fwire_Y, VDD__bar;

	not (int_fwire_Y, A);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module LATCHX1 (Q, D, CLK, VDD, VSS);
	output Q;
	input D, CLK;
	reg notifier = 1'b0;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Q, int_fwire_IQ, int_fwire_Q;
	wire VDD__bar;

	altos_latch (int_fwire_IQ, notifier, CLK, D);
	buf (int_fwire_Q, int_fwire_IQ);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Q, VDD__bar, VSS);
	altos_power_down (Q, int_fwire_Q, __PWD_DWN_OUT__Q);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module MUX2X1 (Y, A, B, S, VDD, VSS);
	output Y;
	input A, B, S;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, A__bar, B__bar;
	wire int_fwire_0, int_fwire_1, int_fwire_Y;
	wire S__bar, VDD__bar;

	not (S__bar, S);
	not (B__bar, B);
	and (int_fwire_0, B__bar, S__bar);
	not (A__bar, A);
	and (int_fwire_1, A__bar, S);
	or (int_fwire_Y, int_fwire_1, int_fwire_0);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module NAND2X1 (Y, A, B, VDD, VSS);
	output Y;
	input A, B;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, A__bar, B__bar;
	wire int_fwire_Y, VDD__bar;

	not (B__bar, B);
	not (A__bar, A);
	or (int_fwire_Y, A__bar, B__bar);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module NAND3X1 (Y, A, B, C, VDD, VSS);
	output Y;
	input A, B, C;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, A__bar, B__bar;
	wire C__bar, int_fwire_Y, VDD__bar;

	not (C__bar, C);
	not (B__bar, B);
	not (A__bar, A);
	or (int_fwire_Y, A__bar, B__bar, C__bar);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module NOR2X1 (Y, A, B, VDD, VSS);
	output Y;
	input A, B;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, A__bar, B__bar;
	wire int_fwire_Y, VDD__bar;

	not (B__bar, B);
	not (A__bar, A);
	and (int_fwire_Y, A__bar, B__bar);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module NOR3X1 (Y, A, B, C, VDD, VSS);
	output Y;
	input A, B, C;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, A__bar, B__bar;
	wire C__bar, int_fwire_Y, VDD__bar;

	not (C__bar, C);
	not (B__bar, B);
	not (A__bar, A);
	and (int_fwire_Y, A__bar, B__bar, C__bar);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module OAI21X1 (Y, A, B, C, VDD, VSS);
	output Y;
	input A, B, C;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, A__bar, B__bar;
	wire C__bar, int_fwire_0, int_fwire_Y;
	wire VDD__bar;

	not (C__bar, C);
	not (B__bar, B);
	not (A__bar, A);
	and (int_fwire_0, A__bar, B__bar);
	or (int_fwire_Y, int_fwire_0, C__bar);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module OAI22X1 (Y, A, B, C, D, VDD, VSS);
	output Y;
	input A, B, C, D;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, A__bar, B__bar;
	wire C__bar, D__bar, int_fwire_0;
	wire int_fwire_1, int_fwire_Y, VDD__bar;

	not (D__bar, D);
	not (C__bar, C);
	and (int_fwire_0, C__bar, D__bar);
	not (B__bar, B);
	not (A__bar, A);
	and (int_fwire_1, A__bar, B__bar);
	or (int_fwire_Y, int_fwire_1, int_fwire_0);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module OR2X1 (Y, A, B, VDD, VSS);
	output Y;
	input A, B;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, int_fwire_Y, VDD__bar;

	or (int_fwire_Y, A, B);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module OR2X2 (Y, A, B, VDD, VSS);
	output Y;
	input A, B;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, int_fwire_Y, VDD__bar;

	or (int_fwire_Y, A, B);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module TBUFX1 (Y, A, EN, VDD, VSS);
	output Y;
	input A, EN;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, int_fwire_Y, VDD__bar;

	notif1 (int_fwire_Y, A, EN);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module XNOR2X1 (Y, A, B, VDD, VSS);
	output Y;
	input A, B;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, A__bar, B__bar;
	wire int_fwire_0, int_fwire_1, int_fwire_Y;
	wire VDD__bar;

	not (B__bar, B);
	not (A__bar, A);
	and (int_fwire_0, A__bar, B__bar);
	and (int_fwire_1, A, B);
	or (int_fwire_Y, int_fwire_1, int_fwire_0);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine

// type:  
`timescale 1ns/10ps
`celldefine
module XOR2X1 (Y, A, B, VDD, VSS);
	output Y;
	input A, B;
	(* pg_type = "primary_power" *) input VDD;
	(* pg_type = "primary_ground" *) input VSS;
`ifdef no_power_gate
	initial force VDD = 1'b1;
	initial force VSS = 1'b0;
`endif


	// Function
	wire __PWD_DWN_OUT__Y, A__bar, B__bar;
	wire int_fwire_0, int_fwire_1, int_fwire_Y;
	wire VDD__bar;

	not (A__bar, A);
	and (int_fwire_0, A__bar, B);
	not (B__bar, B);
	and (int_fwire_1, A, B__bar);
	or (int_fwire_Y, int_fwire_1, int_fwire_0);
	not (VDD__bar, VDD);
	or (__PWD_DWN_OUT__Y, VDD__bar, VSS);
	altos_power_down (Y, int_fwire_Y, __PWD_DWN_OUT__Y);

	// Timing
endmodule
`endcelldefine


`ifdef _udp_power_down
`else
`define _udp_power_down
primitive altos_power_down (o, o_in, pwr_dn);
	output o;
	input o_in, pwr_dn;

	table
		0 0 : 0;
		1 0 : 1;
		x 0 : x;
		? 1 : x;
		? x : x;
	endtable
endprimitive
`endif
`ifdef _udp_def_altos_latch_
`else
`define _udp_def_altos_latch_
primitive altos_latch (q, v, clk, d);
	output q;
	reg q;
	input v, clk, d;

	table
		* ? ? : ? : x;
		? 1 0 : ? : 0;
		? 1 1 : ? : 1;
		? x 0 : 0 : -;
		? x 1 : 1 : -;
		? 0 ? : ? : -;
	endtable
endprimitive
`endif

`ifdef _udp_def_altos_dff_err_
`else
`define _udp_def_altos_dff_err_
primitive altos_dff_err (q, clk, d);
	output q;
	reg q;
	input clk, d;

	table
		(0x) ? : ? : 0;
		(1x) ? : ? : 1;
	endtable
endprimitive
`endif

`ifdef _udp_def_altos_dff_
`else
`define _udp_def_altos_dff_
primitive altos_dff (q, v, clk, d, xcr);
	output q;
	reg q;
	input v, clk, d, xcr;

	table
		*  ?   ? ? : ? : x;
		? (x1) 0 0 : ? : 0;
		? (x1) 1 0 : ? : 1;
		? (x1) 0 1 : 0 : 0;
		? (x1) 1 1 : 1 : 1;
		? (x1) ? x : ? : -;
		? (bx) 0 ? : 0 : -;
		? (bx) 1 ? : 1 : -;
		? (x0) b ? : ? : -;
		? (x0) ? x : ? : -;
		? (01) 0 ? : ? : 0;
		? (01) 1 ? : ? : 1;
		? (10) ? ? : ? : -;
		?  b   * ? : ? : -;
		?  ?   ? * : ? : -;
	endtable
endprimitive
`endif

`ifdef _udp_def_altos_dff_r_err_
`else
`define _udp_def_altos_dff_r_err_
primitive altos_dff_r_err (q, clk, d, r);
	output q;
	reg q;
	input clk, d, r;

	table
		 ?   0 (0x) : ? : -;
		 ?   0 (x0) : ? : -;
		(0x) ?  0   : ? : 0;
		(0x) 0  x   : ? : 0;
		(1x) ?  0   : ? : 1;
		(1x) 0  x   : ? : 1;
	endtable
endprimitive
`endif

`ifdef _udp_def_altos_dff_r_
`else
`define _udp_def_altos_dff_r_
primitive altos_dff_r (q, v, clk, d, r, xcr);
	output q;
	reg q;
	input v, clk, d, r, xcr;

	table
		*  ?   ?  ?   ? : ? : x;
		?  ?   ?  1   ? : ? : 0;
		?  b   ? (1?) ? : 0 : -;
		?  x   0 (1?) ? : 0 : -;
		?  ?   ? (10) ? : ? : -;
		?  ?   ? (x0) ? : ? : -;
		?  ?   ? (0x) ? : 0 : -;
		? (x1) 0  ?   0 : ? : 0;
		? (x1) 1  0   0 : ? : 1;
		? (x1) 0  ?   1 : 0 : 0;
		? (x1) 1  0   1 : 1 : 1;
		? (x1) ?  ?   x : ? : -;
		? (bx) 0  ?   ? : 0 : -;
		? (bx) 1  0   ? : 1 : -;
		? (x0) 0  ?   ? : ? : -;
		? (x0) 1  0   ? : ? : -;
		? (x0) ?  0   x : ? : -;
		? (01) 0  ?   ? : ? : 0;
		? (01) 1  0   ? : ? : 1;
		? (10) ?  ?   ? : ? : -;
		?  b   *  ?   ? : ? : -;
		?  ?   ?  ?   * : ? : -;
	endtable
endprimitive
`endif

`ifdef _udp_def_altos_dff_s_err_
`else
`define _udp_def_altos_dff_s_err_
primitive altos_dff_s_err (q, clk, d, s);
	output q;
	reg q;
	input clk, d, s;

	table
		 ?   1 (0x) : ? : -;
		 ?   1 (x0) : ? : -;
		(0x) ?  0   : ? : 0;
		(0x) 1  x   : ? : 0;
		(1x) ?  0   : ? : 1;
		(1x) 1  x   : ? : 1;
	endtable
endprimitive
`endif

`ifdef _udp_def_altos_dff_s_
`else
`define _udp_def_altos_dff_s_
primitive altos_dff_s (q, v, clk, d, s, xcr);
	output q;
	reg q;
	input v, clk, d, s, xcr;

	table
		*  ?   ?  ?   ? : ? : x;
		?  ?   ?  1   ? : ? : 1;
		?  b   ? (1?) ? : 1 : -;
		?  x   1 (1?) ? : 1 : -;
		?  ?   ? (10) ? : ? : -;
		?  ?   ? (x0) ? : ? : -;
		?  ?   ? (0x) ? : 1 : -;
		? (x1) 0  0   0 : ? : 0;
		? (x1) 1  ?   0 : ? : 1;
		? (x1) 1  ?   1 : 1 : 1;
		? (x1) 0  0   1 : 0 : 0;
		? (x1) ?  ?   x : ? : -;
		? (bx) 1  ?   ? : 1 : -;
		? (bx) 0  0   ? : 0 : -;
		? (x0) 1  ?   ? : ? : -;
		? (x0) 0  0   ? : ? : -;
		? (x0) ?  0   x : ? : -;
		? (01) 1  ?   ? : ? : 1;
		? (01) 0  0   ? : ? : 0;
		? (10) ?  ?   ? : ? : -;
		?  b   *  ?   ? : ? : -;
		?  ?   ?  ?   * : ? : -;
	endtable
endprimitive
`endif

`ifdef _udp_def_altos_dff_sr_err_
`else
`define _udp_def_altos_dff_sr_err_
primitive altos_dff_sr_err (q, clk, d, s, r);
	output q;
	reg q;
	input clk, d, s, r;

	table
		 ?   1 (0x)  ?   : ? : -;
		 ?   0  ?   (0x) : ? : -;
		 ?   0  ?   (x0) : ? : -;
		(0x) ?  0    0   : ? : 0;
		(0x) 1  x    0   : ? : 0;
		(0x) 0  0    x   : ? : 0;
		(1x) ?  0    0   : ? : 1;
		(1x) 1  x    0   : ? : 1;
		(1x) 0  0    x   : ? : 1;
	endtable
endprimitive
`endif

`ifdef _udp_def_altos_dff_sr_0
`else
`define _udp_def_altos_dff_sr_0
primitive altos_dff_sr_0 (q, v, clk, d, s, r, xcr);
	output q;
	reg q;
	input v, clk, d, s, r, xcr;

	table
	//	v,  clk, d, s, r : q' : q;

		*  ?   ?   ?   ?   ? : ? : x;
		?  ?   ?   ?   1   ? : ? : 0;
		?  ?   ?   1   0   ? : ? : 1;
		?  b   ? (1?)  0   ? : 1 : -;
		?  x   1 (1?)  0   ? : 1 : -;
		?  ?   ? (10)  0   ? : ? : -;
		?  ?   ? (x0)  0   ? : ? : -;
		?  ?   ? (0x)  0   ? : 1 : -;
		?  b   ?  0   (1?) ? : 0 : -;
		?  x   0  0   (1?) ? : 0 : -;
		?  ?   ?  0   (10) ? : ? : -;
		?  ?   ?  0   (x0) ? : ? : -;
		?  ?   ?  0   (0x) ? : 0 : -;
		? (x1) 0  0    ?   0 : ? : 0;
		? (x1) 1  ?    0   0 : ? : 1;
		? (x1) 0  0    ?   1 : 0 : 0;
		? (x1) 1  ?    0   1 : 1 : 1;
		? (x1) ?  ?    0   x : ? : -;
		? (x1) ?  0    ?   x : ? : -;
		? (1x) 0  0    ?   ? : 0 : -;
		? (1x) 1  ?    0   ? : 1 : -;
		? (x0) 0  0    ?   ? : ? : -;
		? (x0) 1  ?    0   ? : ? : -;
		? (x0) ?  0    0   x : ? : -;
		? (0x) 0  0    ?   ? : 0 : -;
		? (0x) 1  ?    0   ? : 1 : -;
		? (01) 0  0    ?   ? : ? : 0;
		? (01) 1  ?    0   ? : ? : 1;
		? (10) ?  0    ?   ? : ? : -;
		? (10) ?  ?    0   ? : ? : -;
		?  b   *  0    ?   ? : ? : -;
		?  b   *  ?    0   ? : ? : -;
		?  ?   ?  ?    ?   * : ? : -;
	endtable
endprimitive
`endif

`ifdef _udp_def_altos_dff_sr_1
`else
`define _udp_def_altos_dff_sr_1
primitive altos_dff_sr_1 (q, v, clk, d, s, r, xcr);
	output q;
	reg q;
	input v, clk, d, s, r, xcr;

	table
	//	v,  clk, d, s, r : q' : q;

		*  ?   ?   ?   ?   ? : ? : x;
		?  ?   ?   0   1   ? : ? : 0;
		?  ?   ?   1   ?   ? : ? : 1;
		?  b   ? (1?)  0   ? : 1 : -;
		?  x   1 (1?)  0   ? : 1 : -;
		?  ?   ? (10)  0   ? : ? : -;
		?  ?   ? (x0)  0   ? : ? : -;
		?  ?   ? (0x)  0   ? : 1 : -;
		?  b   ?  0   (1?) ? : 0 : -;
		?  x   0  0   (1?) ? : 0 : -;
		?  ?   ?  0   (10) ? : ? : -;
		?  ?   ?  0   (x0) ? : ? : -;
		?  ?   ?  0   (0x) ? : 0 : -;
		? (x1) 0  0    ?   0 : ? : 0;
		? (x1) 1  ?    0   0 : ? : 1;
		? (x1) 0  0    ?   1 : 0 : 0;
		? (x1) 1  ?    0   1 : 1 : 1;
		? (x1) ?  ?    0   x : ? : -;
		? (x1) ?  0    ?   x : ? : -;
		? (1x) 0  0    ?   ? : 0 : -;
		? (1x) 1  ?    0   ? : 1 : -;
		? (x0) 0  0    ?   ? : ? : -;
		? (x0) 1  ?    0   ? : ? : -;
		? (x0) ?  0    0   x : ? : -;
		? (0x) 0  0    ?   ? : 0 : -;
		? (0x) 1  ?    0   ? : 1 : -;
		? (01) 0  0    ?   ? : ? : 0;
		? (01) 1  ?    0   ? : ? : 1;
		? (10) ?  0    ?   ? : ? : -;
		? (10) ?  ?    0   ? : ? : -;
		?  b   *  0    ?   ? : ? : -;
		?  b   *  ?    0   ? : ? : -;
		?  ?   ?  ?    ?   * : ? : -;
	endtable
endprimitive
`endif

`ifdef _udp_def_altos_latch_r_
`else
`define _udp_def_altos_latch_r_
primitive altos_latch_r (q, v, clk, d, r);
	output q;
	reg q;
	input v, clk, d, r;

	table
		* ? ? ? : ? : x;
		? ? ? 1 : ? : 0;
		? 0 ? 0 : ? : -;
		? 0 ? x : 0 : -;
		? 1 0 0 : ? : 0;
		? 1 0 x : ? : 0;
		? 1 1 0 : ? : 1;
		? x 0 0 : 0 : -;
		? x 0 x : 0 : -;
		? x 1 0 : 1 : -;
	endtable
endprimitive
`endif

`ifdef _udp_def_altos_latch_s_
`else
`define _udp_def_altos_latch_s_
primitive altos_latch_s (q, v, clk, d, s);
	output q;
	reg q;
	input v, clk, d, s;

	table
		* ? ? ? : ? : x;
		? ? ? 1 : ? : 1;
		? 0 ? 0 : ? : -;
		? 0 ? x : 1 : -;
		? 1 1 0 : ? : 1;
		? 1 1 x : ? : 1;
		? 1 0 0 : ? : 0;
		? x 1 0 : 1 : -;
		? x 1 x : 1 : -;
		? x 0 0 : 0 : -;
	endtable
endprimitive
`endif

`ifdef _udp_def_altos_latch_sr_0
`else
`define _udp_def_altos_latch_sr_0
primitive altos_latch_sr_0 (q, v, clk, d, s, r);
	output q;
	reg q;
	input v, clk, d, s, r;

	table
		* ? ? ? ? : ? : x;
		? 1 1 ? 0 : ? : 1;
		? 1 0 0 ? : ? : 0;
		? ? ? 1 0 : ? : 1;
		? ? ? ? 1 : ? : 0;
		? 0 * ? ? : ? : -;
		? 0 ? * 0 : 1 : 1;
		? 0 ? 0 * : 0 : 0;
		? * 1 ? 0 : 1 : 1;
		? * 0 0 ? : 0 : 0;
		? ? 1 * 0 : 1 : 1;
		? ? 0 0 * : 0 : 0;
	endtable
endprimitive
`endif

`ifdef _udp_def_altos_latch_sr_1
`else
`define _udp_def_altos_latch_sr_1
primitive altos_latch_sr_1 (q, v, clk, d, s, r);
	output q;
	reg q;
	input v, clk, d, s, r;

	table
		* ? ? ? ? : ? : x;
		? 1 1 ? 0 : ? : 1;
		? 1 0 0 ? : ? : 0;
		? ? ? 1 ? : ? : 1;
		? ? ? 0 1 : ? : 0;
		? 0 * ? ? : ? : -;
		? 0 ? * 0 : 1 : 1;
		? 0 ? 0 * : 0 : 0;
		? * 1 ? 0 : 1 : 1;
		? * 0 0 ? : 0 : 0;
		? ? 1 * 0 : 1 : 1;
		? ? 0 0 * : 0 : 0;
	endtable
endprimitive
`endif
