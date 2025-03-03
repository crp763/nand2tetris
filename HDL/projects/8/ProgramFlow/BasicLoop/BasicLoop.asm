// push constant 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop local 0
@0
D=A
@LCL
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
(BasicLoop$LOOP)
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
// push local 0
@0
D=A
@LCL
AD=M-D
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
// pop local 0
@0
D=A
@LCL
AD=M-D
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
// if-goto LOOP
@SP
AM=M-1
D=M
@BasicLoop$LOOP
D;JNE
// push local 0
@0
D=A
@LCL
AD=M-D
D=M
@SP
A=M
M=D
@SP
M=M+1
