// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

// Uses successive addition and bit-shift operations to calcualte R0*R1
// Ignores leftmost bit since program is meant for strictly positive inputs only
// Bit shifts start from the most significant bit of R1
// R0 is added to R2 if R1&(2^15) is positive
// R2 is then doubled whenever the loop restarts and checks the next bit of R1

// Initialize result as 0
@R2
M=0

// Store the current bit of R1 we are checking in R3
@15
D=A
@R3
M=D

// Calculate and store 2^15=32768 in R4 by doubling 2^14=16384, because we can't @32768 directly (out of memory range allowed by compiler)
@16384
D=A
D=D+A
@R4
M=D


(LOOP)
    // Left-shift R1 and R2
    @R1
    D=M
    M=D+M
    @R2
    D=M
    M=D+M

    // Check what is now 16th bit of R1, if it's 1 then add R0 to R2
    @R4
    D=M
    @R1
    D=D&M
    @CHCK
    D;JEQ // Skip addition step if 15th bit was 0
    
    // Add R0 to R2
    @R0
    D=M
    @R2
    M=D+M

    (CHCK)
    // Decrement R3, then jump back to start of loop if result is greater than 0
    @R3
    MD=M-1
    @LOOP
    D;JGT

(END)
@END
0;JMP
