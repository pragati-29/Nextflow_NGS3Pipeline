#!/bin/bash -ue
if [ "sample"/**R1_001.fastq.gz =~ "FEV2F2both"]
then
echo "sample" > out_test.txt 
fi
