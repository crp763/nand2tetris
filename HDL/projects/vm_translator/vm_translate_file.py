#!/usr/bin/python3

# TODO:
# Check for duplicate function names

import sys
import re
import os

n_args = len(sys.argv)

######################
## Input Validation ##
######################

# Check if input file was passed as an argument
if n_args >= 2:
    f_in = sys.argv[1]
else:
    f_in = input('Enter the name of the file you wish to assemble: ')

# Make sure input file exists, prompt for new file if it does not
while not os.path.isfile(f_in):
    print('File not found: ', f_in)
    f_in = input('Enter the name of the file you wish to assemble: ')
f_in_pre = re.sub('\.vm$','',f_in)
f_in_pre = re.sub('.+/','',f_in_pre)

# Check if output file name was passed as an argument
if n_args >= 3:
    f_out = sys.argv[2]
else:
    f_out = input('Enter the name of the output file: ')

debug = False
overwrite=0
if n_args >=4:
    for arg in sys.argv[3:]:
        if arg == '-debug':
            debug = True
        if arg == '-overwrite':
            overwrite = 1


# Check if output file exists, and if the user wants to overwrite or create a new file
while os.path.isfile(f_out) and (overwrite == 0):
    print('The specified output file already exists: ')
    print(f_out)
    inp=input('Overwrite? [y/n]: ')
    if re.search('^[yY]([eE][sS])*$',inp):
        overwrite=1
    elif re.search('^[nN][oO]*$',inp):
        f_out=input('Enter name of output file: ')
    else:
        print('Input not recognized')

fid_out = open(f_out,'w')

###########################
## Compile regex objects ##
###########################

# Stack control
push_re = re.compile('^push +(\S+) +(\S+)$')
pop_re = re.compile('^pop +(\S+) +(\S+)$')

# Flow control
label_re = re.compile('^label +([a-zA-Z_\.:][a-zA-Z_\.:0-9]*)$')
goto_re = re.compile('^goto +([a-zA-Z_\.:][a-zA-Z_\.:0-9]*)$')
if_goto_re = re.compile('^if-goto +([a-zA-Z_\.:][a-zA-Z_\.:0-9]*)$')

# Function calls
function_re = re.compile('^function +(\S+) +(\S+)$')
call_re = re.compile('^call +(\S+) +(\S+)$')

###########################
## Function Declarations ##
###########################

# Push value from D register to top of stack
def push_D(fid):
    fid.write('@SP\n')
    fid.write('A=M\n')
    fid.write('M=D\n')
    fid.write('@SP\n')
    fid.write('M=M+1\n')

# Pop value from top of stack and place into D register
def pop_D(fid):
    fid.write('@SP\n')
    fid.write('AM=M-1\n')
    fid.write('D=M\n')

# Move value from D register into the memory address stored in R13
def point_D_R13(fid):
    fid.write('@R13\n')
    fid.write('A=M\n')
    fid.write('M=D\n')

# Calculate address of (segment base) + index, store in D register
def calc_seg_AD(segment,index,fid):
    index = int(index)
    if index > 0:
        fid.write(f'@{index}\n')
        fid.write('D=A\n')
        fid.write(f'@{segment}\n')
        fid.write('AD=D+M\n')
    else:
        fid.write(f'@{-index}\n')
        fid.write('D=A\n')
        fid.write(f'@{segment}\n')
        fid.write('AD=M-D\n')

# Store the value in the D register in R13
def store_D_R13(fid):
    fid.write('@R13\n')
    fid.write('M=D\n')

# Load the value in R13 into the D register
def load_R13_D(fid):
    fid.write('@R13\n')
    fid.write('D=M\n')

# Compare top two values on stack
def comp_stack(jmp,n,fid):
    comp_label = f'{f_in_pre}.COMP_{n}'
    end_label = f'{f_in_pre}.END_{n}'
    pop_D(fid)
    fid.write('@SP\n')
    fid.write('AM=M-1\n')
    fid.write('D=M-D\n')
    fid.write(f'@{comp_label}\n')
    fid.write(f'D;{jmp}\n')
    fid.write('D=0\n')
    fid.write(f'@{end_label}\n')
    fid.write('0;JMP\n')
    fid.write(f'({comp_label})\n')
    fid.write('D=-1\n')
    fid.write(f'({end_label})\n')
    push_D(fid)

# Treat R14 as register and pop stack to D (identical to pop_D, but uses R14
# instead of SP). Used for unwind the frame stack during return statements
def pop_R14_to_D(fid):
    fid.write('@R14\n')
    fid.write('AM=M-1\n')
    fid.write('D=M\n')

########################################
## Convert vm instruction to assembly ##
########################################

print(f'Translating {f_in}...')

line_num = 0
n_comp = 0
function_returns = 0

# Need to create a list to contain the name of the current script or function
# Will be used to create unique names for labels
# Upon entering a script or function, name is appended
# Upon hitting a return statement, last name added is popped
function_names = list()
function_names.append(f_in_pre)

fid_in = open(f_in,'r')


for line_orig in fid_in:
    
    line_num += 1
    
    line = re.sub('//.*','',line_orig)    # Remove comments
    line = re.sub('[\r\n\t]','',line)    # Remove newline and tab characters
    line = line.strip()    # Remove leading and trailing spaces
    
    if line:
        if debug:
            fid_out.write(f'// {line}\n')
    
    # Push operations
    if (push_txt := push_re.match(line)):   # if push instruction
        
        stack = push_txt.group(1)
        value = push_txt.group(2)
        
        if stack == 'constant':
            fid_out.write(f'@{value}\n')
            fid_out.write('D=A\n')
        elif stack == 'local':
            calc_seg_AD('LCL',value,fid_out)
            fid_out.write('D=M\n')
        elif stack == 'argument':
            calc_seg_AD('ARG',value,fid_out)
            fid_out.write('D=M\n')
        elif stack == 'this':
            calc_seg_AD('THIS',value,fid_out)
            fid_out.write('D=M\n')
        elif stack == 'that':
            calc_seg_AD('THAT',value,fid_out)
            fid_out.write('D=M\n')
        elif stack == 'static':
            fid_out.write(f'@{f_in_pre + "." + value}\n')
            fid_out.write('D=M\n')
        elif stack == 'pointer':
            fid_out.write(f'@{3 + int(value)}\n')
            fid_out.write('D=M\n')
        elif stack == 'temp':
            fid_out.write(f'@{5 + int(value)}\n')
            fid_out.write('D=M\n')
        
        push_D(fid_out)
    
    # Pop operations
    elif (pop_txt := pop_re.match(line)):    # if pop instruction
    
        stack = pop_txt.group(1)
        value = pop_txt.group(2)
        
        if stack == 'constant':
            pop_D(fid_out)
            fid_out.write(f'@{value}\n')
            fid_out.write('M=D\n')
        elif stack == 'local':
            calc_seg_AD('LCL',value,fid_out)
            store_D_R13(fid_out)
            pop_D(fid_out)
            point_D_R13(fid_out)
        elif stack == 'argument':
            calc_seg_AD('ARG',value,fid_out)
            store_D_R13(fid_out)
            pop_D(fid_out)
            point_D_R13(fid_out)
        elif stack == 'this':
            calc_seg_AD('THIS',value,fid_out)
            store_D_R13(fid_out)
            pop_D(fid_out)
            point_D_R13(fid_out)
        elif stack == 'that':
            calc_seg_AD('THAT',value,fid_out)
            store_D_R13(fid_out)
            pop_D(fid_out)
            point_D_R13(fid_out)
        elif stack == 'static':
            pop_D(fid_out)
            fid_out.write(f'@{f_in_pre + "." + value}\n')
            fid_out.write('M=D\n')
        elif stack == 'pointer':
            pop_D(fid_out)
            fid_out.write(f'@{3 + int(value)}\n')
            fid_out.write('M=D\n')
        elif stack == 'temp':
            pop_D(fid_out)
            fid_out.write(f'@{5 + int(value)}\n')
            fid_out.write('M=D\n')
    
    # Arithmetic and logic operations
    elif line == 'add':
        pop_D(fid_out)
        fid_out.write('@SP\n')
        fid_out.write('AM=M-1\n')
        fid_out.write('D=D+M\n')
        push_D(fid_out)
    elif line == 'sub':
        pop_D(fid_out)
        fid_out.write('@SP\n')
        fid_out.write('AM=M-1\n')
        fid_out.write('D=M-D\n')
        push_D(fid_out)
    elif line == 'neg':
        fid_out.write('@SP\n')
        fid_out.write('A=M-1\n')
        fid_out.write('M=-M\n')
    elif line == 'eq':
        comp_stack('JEQ',n_comp,fid_out)
        n_comp += 1
    elif line == 'gt':
        comp_stack('JGT',n_comp,fid_out)
        n_comp += 1
    elif line == 'lt':
        comp_stack('JLT',n_comp,fid_out)
        n_comp += 1
    elif line == 'and':
        pop_D(fid_out)
        fid_out.write('@SP\n')
        fid_out.write('AM=M-1\n')
        fid_out.write('D=D&M\n')
        push_D(fid_out)
    elif line == 'or':
        pop_D(fid_out)
        fid_out.write('@SP\n')
        fid_out.write('AM=M-1\n')
        fid_out.write('D=D|M\n')
        push_D(fid_out)
    elif line == 'not':
        fid_out.write('@SP\n')
        fid_out.write('A=M-1\n')
        fid_out.write('M=!M\n')    
    
    # Function operations
    elif (label_txt := label_re.match(line)):
        label = label_txt.group(1)
        fid_out.write(f'({function_names[-1]}${label})\n')
    elif (goto_txt := goto_re.match(line)):
        label = goto_txt.group(1)
        fid_out.write(f'@{function_names[-1]}${label}\n')
        fid_out.write('0;JMP\n')
    elif (if_goto_txt := if_goto_re.match(line)):
        label = if_goto_txt.group(1)
        pop_D(fid_out)
        fid_out.write(f'@{function_names[-1]}${label}\n')
        fid_out.write('D;JNE\n')
    elif (function_txt := function_re.match(line)):
        function_names.append(function_txt.group(1))
        n_vars = int(function_txt.group(2))
        # (f)
        fid_out.write(f'({function_names[-1]})\n')
        # Push zero to stack n_vars times
        # Calling push_D() repeatedly is not efficient
        # We can optimize by first pushing all our 0's, and only updating the value of @SP at the very end
        if n_vars > 0:
            fid_out.write('D=0\n')
            fid_out.write('@SP\n')
            fid_out.write('A=M\n')
            for i in range(n_vars):
                fid_out.write('M=0\n')
                fid_out.write('A=A+1\n')
            fid_out.write('D=A\n')
            fid_out.write('@SP\n')
            fid_out.write('M=D\n')
    elif (call_txt := call_re.match(line)):
        function_name = call_txt.group(1)
        n_args = int(call_txt.group(2))
        # Push RET
        fid_out.write(f'@{function_name}$ret_{f_in_pre}_{function_returns}\n')
        fid_out.write('D=A\n')
        push_D(fid_out)
        # Push LCL
        fid_out.write('@LCL\n')
        fid_out.write('D=M\n')
        push_D(fid_out)
        # Push ARG
        fid_out.write('@ARG\n')
        fid_out.write('D=M\n')
        push_D(fid_out)
        # Push THIS
        fid_out.write('@THIS\n')
        fid_out.write('D=M\n')
        push_D(fid_out)
        # Push THAT
        fid_out.write('@THAT\n')
        fid_out.write('D=M\n')
        push_D(fid_out)
        # ARG = SP-n-5
        fid_out.write(f'@{n_args+5}\n')
        fid_out.write('D=A\n')
        fid_out.write('@SP\n')
        fid_out.write('D=M-D\n')
        fid_out.write('@ARG\n')
        fid_out.write('M=D\n')
        # LCL = SP
        fid_out.write('@SP\n')
        fid_out.write('D=M\n')
        fid_out.write('@LCL\n')
        fid_out.write('M=D\n')
        # goto function
        fid_out.write(f'@{function_name}\n')
        fid_out.write('0;JMP\n')
        # (return-address)
        fid_out.write(f'({function_name}$ret_{f_in_pre}_{function_returns})\n')
        function_returns += 1
    elif line == 'return':
        # Restore the frame of the previous function
        # According to the Hack specification, the information on the previous
        # function's frame is stored before the LCL stack
        # Function stacks are ordered as follows: ARG->FRAME->LCL->SP
        # Pop last function name from file list
        function_names.pop()
        # FRAME=LCL will be stored in R14, will be unwound with pop_R14_to_D()
        fid_out.write('@LCL\n')
        fid_out.write('D=M\n')
        fid_out.write('@R14\n')
        fid_out.write('M=D\n')
        # RET=*(FRAME-5) will be stored in R15
        calc_seg_AD('R14',-5,fid_out)
        fid_out.write('D=M\n')
        fid_out.write('@R15\n')
        fid_out.write('M=D\n')
        # *ARG = pop(), will position our return value at @SP once frame is restored
        pop_D(fid_out)
        fid_out.write('@ARG\n')
        fid_out.write('A=M\n')
        fid_out.write('M=D\n')
        # SP = ARG+1
        fid_out.write('@ARG\n')
        fid_out.write('D=M\n')
        fid_out.write('@SP\n')
        fid_out.write('M=D+1\n')
        # In the frame stack, information is ordered RET->LCL->ARG->THIS->THAT
        # THAT, THIS, LCL, ARG, RET are unwound starting at FRAME=LCL-1
        pop_R14_to_D(fid_out) # FRAME-1
        fid_out.write('@THAT\n')
        fid_out.write('M=D\n')
        pop_R14_to_D(fid_out) # FRAME-2
        fid_out.write('@THIS\n')
        fid_out.write('M=D\n')
        pop_R14_to_D(fid_out) # FRAME-3
        fid_out.write('@ARG\n')
        fid_out.write('M=D\n')
        pop_R14_to_D(fid_out) # FRAME-4
        fid_out.write('@LCL\n')
        fid_out.write('M=D\n')
        # goto RET, which we stored in R15
        fid_out.write('@R15\n') # FRAME-5
        fid_out.write('A=M;JMP\n')
    
fid_out.close()
