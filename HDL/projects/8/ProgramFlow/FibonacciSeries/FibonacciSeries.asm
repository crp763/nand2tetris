// push argument 1
@1
D=A
@ARG
AD=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
// pop pointer 1
@SP
AM=M-1
D=M
@4
M=D
// push constant 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop that 0
@0
D=A
@THAT
AD=M-D
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
// push constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop that 1
@1
D=A
@THAT
AD=D+M
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
// push argument 0
@0
D=A
@ARG
AD=M-D
D=M
@SP
A=M
M=D
@SP
M=M+1
// push constant 2
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
AM=M-1
D=M
@SP
AM=M-1
D=M-D
@SP
A=M
M=D
@SP
M=M+1
// pop argument 0
@0
D=A
@ARG
AD=M-D
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
// label LOOP
(FibonacciSeries$LOOP)
// push argument 0
@0
D=A
@ARG
AD=M-D
D=M
@SP
A=M
M=D
@SP
M=M+1
// if-goto COMPUTE_ELEMENT
@SP
AM=M-1
D=M
@FibonacciSeries$COMPUTE_ELEMENT
D;JNE
// goto END
@FibonacciSeries$END
0;JMP
// label COMPUTE_ELEMENT
(FibonacciSeries$COMPUTE_ELEMENT)
// push that 0
@0
D=A
@THAT
AD=M-D
D=M
@SP
A=M
M=D
@SP
M=M+1
// push that 1
@1
D=A
@THAT
AD=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
AM=M-1
D=M
@SP
AM=M-1
D=D+M
@SP
A=M
M=D
@SP
M=M+1
// pop that 2
@2
D=A
@THAT
AD=D+M
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
// push pointer 1
@4
D=M
@SP
A=M
M=D
@SP
M=M+1
// push constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
AM=M-1
D=M
@SP
AM=M-1
D=D+M
@SP
A=M
M=D
@SP
M=M+1
// pop pointer 1
@SP
AM=M-1
D=M
@4
M=D
// push argument 0
@0
D=A
@ARG
AD=M-D
D=M
@SP
A=M
M=D
@SP
M=M+1
// push constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
AM=M-1
D=M
@SP
AM=M-1
D=M-D
@SP
A=M
M=D
@SP
M=M+1
// pop argument 0
@0
D=A
@ARG
AD=M-D
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
// goto LOOP
@FibonacciSeries$LOOP
0;JMP
// label END
(FibonacciSeries$END)
