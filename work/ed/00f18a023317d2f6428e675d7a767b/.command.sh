#!/bin/bash -ue
if [[ sample/*.fastq.gz =~ "FEV2F2both"]]
then
echo "sample" > out_test.txt 
fi
