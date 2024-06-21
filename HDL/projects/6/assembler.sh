#!/bin/bash


######################
## Input validation ##
######################

# Check for input file argument
if [[ "$#" -ge 1 ]]; then
    f_in=$1
else
    read -p "Enter name of hack assembly file to assemble: " f_in
fi

# Check if input file exists, if not then prompt for new file
while [[ ! -f $f_in ]]; do
    echo "File not found: $f_in"
    read -p "Enter name of hack assembly file to assemble: " f_in
done

# Check for out file argument
if [[ "$#" -ge 2 ]]; then
    f_out=$2
else
    read -p "Enter name of output file: " f_out
fi

# Check if input file exists, if it does then prompt for overwrite, new file, or exit
inp=0
overwrite=0
while [[ -f $f_out ]] && [[ $overwrite = 0 ]]; do
    read -p "Output file already exists, overwrite? [yes/no]: " inp
    if [[ $inp =~ ^[yY]([eE][sS])*$ ]]; then
        overwrite=1
    elif [[ $inp =~ ^[nN][oO]*$ ]]; then
        read -p "Enter name of output file: " f_out
    else
        echo "Input not recognized"
    fi
done
> $f_out


###############
## Functions ##
###############

# Function to check if table contains a given entry. If it does, return the corresponding value
table_lookup () {
    local -n array_text=$2
    local -n array_vals=$3
    ind=0
    for i in ${array_text[@]}
    do
        if [[ $1 = $i ]]; then
            return 0
        fi
        ((ind++))
    done
    return 1
}
##########################
## Create lookup tables ##
##########################

echo "initializing lookup tables..."

# Symbol table
sym_keys=( R0 R1 R2 R3 R4 R5 R6 R7 R8 R9 R10 R11 R12 R13 R14 R15 SP LCL ARG THIS THAT SCREEN KBD   )
sym_vals=( 0  1  2  3  4  5  6  7  8  9  10  11  12  13  14  15  0  1   2   3    4    16384  24576 )

# Destination table
dst_keys=( 'M='  'D='  'MD=' 'A='  'AM=' 'AD=' 'AMD=' )
dst_vals=( 001   010   011   100   101   110   111    )

# ALU table
alu_keys=( '0'     '1'     '-1'    'D'     'A'     '!D'    '!A'    \
           '-D'    '-A'    'D+1'   'A+1'   'D-1'   'A-1'   'D+A'   \
           'D-A'   'A-D'   'D&A'   'D|A'   'M'     '!M'    '-M'    \
           'M+1'   'M-1'   'D+M'   'D-M'   'M-D'   'D&M'   'D|M'   )
alu_vals=( 0101010 0111111 0111010 0001100 0110000 0001101 0110001 \
           0001111 0110011 0011111 0110111 0001110 0110010 0000010 \
           0010011 0000111 0000000 0010101 1110000 1110001 1110011 \
           1110111 1110010 1000010 1010011 1000111 1000000 1010101 )

# Jump table
jmp_keys=( ';JGT' ';JEQ' ';JGE' ';JLT' ';JNE' ';JLE' ';JMP' )
jmp_vals=(  001    010    011    100    101    110    111   )

#####################
## Resolve symbols ##
#####################

echo "resolving symbols..."

line_num=0;  # Counter to keep track of current line number
instr=0;     # Counter to keep track of instruction number. Increments by 1 after each instruction is found
last_loop=0; # Value of last loop label that was encountered. At the end, the program will check that at least 1 instruction was defined after the final loop label 

# First pass:
# - Determine if a line contains an instruction, if it does then iterate instruction counter by 1
# - If a jump label is encountered, add it to the symbol table and assign it a value equal to the instruction counter + 1
#   - Make sure to check that a valid instruction appears after the last jump label is encountered
# - If a variable label is encountered that does not exist in the symbol table, append the table and assign it the next available memory value
while read -r line; do
    ((line_num++))
    
    line=$(sed 's|//.*||g' <<< $line) # Remove comments
    line=$(sed 's|\s||g' <<< $line)   # Remove whitespace
        
    if [[ $line =~ ^\([a-zA-Z_\.:\$][a-zA-Z_\.:\$0-9]*\)$ ]]; then      # if loop label
        label=${line:1:-1}
        if ! table_lookup $label sym_keys sym_vals; then
            sym_keys+=($label)
            sym_vals+=($instr)
            last_loop=$instr
        fi
        
    elif [[ $line =~ ^@[a-zA-Z_\.:\$][a-zA-Z_\.:\$0-9]*$ ]]; then       # else if symbolic A instruction
        
        ((instr++))
        
    elif [[ ! -z $line ]]; then                             # else if any other instruction
        ((instr++))
        
    fi
    
done < $f_in

if [ $last_loop = $instr ]; then
    echo "ERROR: No valid instructions found after final loop label"
fi

echo ${sym_keys[@]}
echo ${sym_vals[@]}

#######################
## Convert to opcode ##
#######################

echo "writing opcode instructions..."

line_num=0;  # Counter to keep track of current line number
sym_mem=16;  # Counter to keep track of memory space to reserve for new variable symbols

while read -r line
do
    ((line_num++))
    orig_line=$line
    
    line=$(sed 's|//.*||g' <<< $line) # Remove comments
    line=$(sed 's|\s||g' <<< $line)   # Remove whitespace
        
    if [[ $line =~ ^\([a-zA-Z_\.:\$][a-zA-Z_\.:\$0-9]*\)$ ]]; then  # if loop label, do nothing
        true
    elif [[ $line =~ ^@[a-zA-Z_\.:\$][a-zA-Z_\.:\$0-9]*$ ]]; then   # else if symbolic A instruction, look up symbol table and write opcode
        label=${line:1}
        if ! table_lookup $label sym_keys sym_vals; then
            address=$sym_mem
            sym_keys+=($label)
            sym_vals+=($((sym_mem++)))
        else
            address=${sym_vals[$ind]}
        fi
        perl -e 'printf "%016b\n"',$address >> $f_out
    elif [[ $line =~ ^@[0-9]+$ ]]; then                             # else if numeric A instruction, write number out as opcode
        address=${line:1}
        perl -e 'printf "%016b\n"',$address >> $f_out
    elif [[ ! -z $line ]]; then                                     # else check for valid C instruction

        # Check for destination instruction
        dst_val=000
        if [[ $line =~ ^[AMD]+= ]]; then
            if table_lookup $BASH_REMATCH dst_keys dst_vals; then
                dst_str=${dst_keys[$ind]}
                dst_val=${dst_vals[$ind]}
                line=$(sed "s/$dst_str//g" <<< $line)
            else
                echo "ERROR! Invalid destination instruction on line $line_num"
                echo "$orig_line"
                exit 1
            fi
        fi

        # Check for jump instruction
        jmp_val=000
        if [[ $line =~ \;[A-Z]+$ ]]; then
            if table_lookup $BASH_REMATCH jmp_keys jmp_vals; then
                jmp_str=${jmp_keys[$ind]}
                jmp_val=${jmp_vals[$ind]}
                line=$(sed "s/$jmp_str//g" <<< $line)
            else
                echo "ERROR! Invalid jump instruction on line $line_num"
                echo "$orig_line"
                exit 1
            fi
        fi
        
        # Check for ALU instruction (all other text should have been removed)
        if table_lookup $line alu_keys alu_vals; then
            alu_val=${alu_vals[$ind]}
        else
            echo "orig line: $orig_line"
            echo "$orig_line"
            exit 1
        fi
    
    printf '%s%s%s%s\n' 111 $alu_val $dst_val $jmp_val >> $f_out
    
    fi
done < $f_in
