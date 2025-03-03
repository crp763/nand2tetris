#!/usr/bin/python3

import sys
import os
import re

n_args = len(sys.argv)

# Check if output file name was passed as an argument
if n_args >= 2:
    f_out = sys.argv[1]
else:
    f_out = input('Enter the name of the output file: ')

# Make sure Sys.vm file exists
if os.path.isfile('Sys.vm'):
    path = os.path.dirname(os.path.abspath(__file__))
    f_bootstrap_vm = path + '/bootstrap.vm'
    os.system(f'cat {f_bootstrap_vm} > {f_out}')
    os.system(f'vm_translate_file.py Sys.vm Sys.asm -debug -overwrite')
    os.system(f'cat Sys.asm >> {f_out}')
else:
    sys.exit('ERROR: Sys.vm not found')
    
for file in os.listdir('.'):
    if file.endswith('.vm') and file != 'Sys.vm':
        f_out_i = re.sub('\.vm$','.asm',file)
        os.system(f'vm_translate_file.py {file} {f_out_i} -debug -overwrite')
        os.system(f'cat {f_out_i} >> {f_out}')

sys.stdout.write('Complete\n')
        