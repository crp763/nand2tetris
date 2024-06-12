// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

(START)
    @SCREEN // First address of memory block reserved for screen, which is 256x512 pixels, stored in 8k of data. For each pixel, 0=white and 1=black
    D=A
    @i // Stores memory value of current screen pixel
    M=D

(INPUT)
    @KBD // memory address reserved for keyboard, which immediately follows the block of memory reserved for the screen
    D=M
    @BLACK
    D;JGT // If there was any keyboard input, set pixel color register to black
    @WHITE
    D;JEQ // If there was no keyboard input, set pixel color register to white

(BLACK) // Sets color register to black (all ones)
    @color
    M=-1
    @RECOLOR
    0;JMP

(WHITE) // Sets color register to white (all zeros)
    @color
    M=0
    @RECOLOR
    0;JMP

(RECOLOR)
    // Color current pixel
    @color
    D=M
    @i
    A=M
    M=D
    
    // Iterate to next pixel, unless we've passed the last screen memory address and reached @KBD
    @KBD
    D=A
    @i
    M=M+1
    D=D-M
    @START
    D;JEQ // Restart program if we've reached the end of the screen memory
    @RECOLOR
    0;JMP // Otherwise, keep coloring pixels
