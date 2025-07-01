#!/usr/bin/env python3

import os

# Rename files with -S1 before _R1
for file in os.listdir('.'):
    if '_R1' in file:
        new_name = file.replace('_R1', '-S1_R1')
        os.rename(file, new_name)

# Rename files with -S1 before _R2
for file in os.listdir('.'):
    if '_R2' in file:
        new_name = file.replace('_R2', '-S1_R2')
        os.rename(file, new_name)
