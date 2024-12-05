#!/bin/bash -ue
if [ sample == *"CT"* && sample == *"ST8"* && sample == *"ct"* && sample == *"st8"* ] 
then 
bs upload dataset --project="439358924" *R1_001.fastq.gz *R2_001.fastq.gz 
else 
bs upload dataset --project="439358925" *R1_001.fastq.gz *R2_001.fastq.gz 
fi
