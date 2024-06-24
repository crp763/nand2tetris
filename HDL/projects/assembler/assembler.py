#!/usr/bin/python3

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

# Check if output file name was passed as an argument
if n_args >= 3:
    f_out = sys.argv[2]
else:
    f_out = input('Enter the name of the output file: ')

# Check if output file exists, and if the user wants to overwrite or create a new file
overwrite=0
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

##########################
## Create lookup tables ##
##########################

print("Creating lookup tables...")

cur_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

fid_sym = open(cur_dir + '/instruction_tables/symbols.txt','r')
text = fid_sym.read()
lines = text.splitlines()
sym_table = {}
for line in lines:
    fields = line.split(' ')
    sym_table[fields[0]] = format(int(fields[-1]),'016b')
fid_sym.close()

fid_dst = open(cur_dir + '/instruction_tables/destinations.txt','r')
text = fid_dst.read()
lines = text.splitlines()
dst_table = {}
for line in lines:
    fields = line.split(' ')
    dst_table[fields[0]] = fields[-1]
fid_dst.close()

fid_alu = open(cur_dir + '/instruction_tables/arithmetic.txt','r')
text = fid_alu.read()
lines = text.splitlines()
alu_table = {}
for line in lines:
    fields = line.split(' ')
    alu_table[fields[0]] = fields[-1]
fid_alu.close()

fid_jmp = open(cur_dir + '/instruction_tables/jumps.txt','r')
text = fid_jmp.read()
lines = text.splitlines()
jmp_table = {}
for line in lines:
    fields = line.split(' ')
    jmp_table[fields[0]] = fields[-1]
fid_jmp.close()

###########################
## Compile regex objects ##
###########################

loop_label_re = re.compile('^\([a-zA-Z_\.:\$][a-zA-Z_\.:\$0-9]*\)$')
sym_a_inst_re = re.compile('^@[a-zA-Z_\.:\$][a-zA-Z_\.:\$0-9]*$')
num_a_inst_re = re.compile('^@[0-9]+$')
dst_c_inst_re = re.compile('^[AMD]+=')
jmp_c_inst_re = re.compile('\;[A-Z]+$')

##################################
## Add loop labels to sym table ##
##################################

print("Resolving loop labels...")

fid_in = open(f_in,'r')
line_num = 0    # Track line numbers
instr = 0       # Track number of A or C instructions
last_loop = 0   # Used to check if a valid A or C instruction occurs after final loop label

for line_orig in fid_in:

    line_num += 1

    line = re.sub('//.*','',line_orig)    # Remove comments
    line = re.sub('[\s\r\n]','',line)    # Remove whitespace

    if loop_label_re.search(line):   # if loop label, add to symbol table
        label = line[1:-1]
        if not label in sym_table:
            sym_table[label] = format(instr,'016b')
        else:
            print('ERROR! Loop label',line,'at line',line_num,'has already been defined')
            sys.exit('Exiting...')
    elif line.startswith('('):
        print('ERROR: Invalid loop label',line,'encountered on line',line_num)
        print('Loop labels can only contain letters, digit, or the following characters: . _ : $]')
        print('Loop labels cannot start with a number')
        sys.exit('Exiting...')
    elif line:    # if line isn't blank or a loop label, assume it's a valid instruction
        instr += 1

if last_loop == instr:
    print('ERROR! No instructions are defined after the final loop label. All loop labels must be followed by at least 1 instruction')
    sys.exit('Exiting...')


#####################################
## Convert instructions to opcodes ##
#####################################

print("Assembling...")

line_num = 0
sym_mem = 16

fid_in.seek(0)

for line_orig in fid_in:

    line_num += 1

    line = re.sub('//.*','',line_orig)    # Remove comments
    line = re.sub('[\s\r\n]','',line)    # Remove whitespace

    if loop_label_re.search(line):   # if loop label, do nothing
        pass
    elif sym_a_inst_re.search(line):   # if symbolic A instruction, look up symbol table and write opcode
        label = line[1:]
        if label in sym_table:
            fid_out.write(f'{sym_table[label]}\n')
        else:
            sym_table[label] = format(sym_mem,'016b')
            fid_out.write(f'{sym_table[label]}\n')
            sym_mem += 1
    elif num_a_inst_re.search(line):    # if numeric opcode, convert decimal number to binary and write out opcode
        label = line[1:]
        fid_out.write(f'{int(label):016b}\n')
    elif line.startswith('@'):
        print('ERROR: Invalid A instruction',line,'encountered on line',line_num)   # If invalid A instruction, throw error
        print('Symbolic labels can only contain letters, digit, or the following characters: . _ : $]')
        print('Labels cannot start with a number')
        sys.exit('Exiting...')
    elif line:    # If line isn't blank, it should be a C instruction
        # Check for valid dst instruction
        dst_re = dst_c_inst_re.search(line)
        if dst_re:
            dst_key = dst_re.group(0)
            if dst_key in dst_table:
                dst_val = dst_table[dst_key]
                line = line.replace(dst_key,'')
            else:
                print('ERROR! Invalid destination instruction',dst_key[1:-1],'encountered on line',line_num)
                sys.exit('Exiting...')
        else:
            dst_val = '000'
        
        # Check for valid jump instruction
        jmp_re = jmp_c_inst_re.search(line)
        if jmp_re:
            jmp_key = jmp_re.group(0)
            if jmp_key in jmp_table:
                jmp_val = jmp_table[jmp_key]
                line = line.replace(jmp_key,'')
            else:
                print(f'ERROR! Invalid jump instruction {jmp_key[2:]} encountered on line {line_num}')
                sys.exit('Exiting...')
        else:
            jmp_val = '000'
        
        # Remaining text should be an alu instruction
        if line in alu_table:
            alu_val = alu_table[line]
            fid_out.write(f'111{alu_val}{dst_val}{jmp_val}\n')
        else:
            print(f'ERROR! Invalid instruction {line_orig} encountered on line {line_num}')
            sys.exit('Exiting...')

fid_out.close()

