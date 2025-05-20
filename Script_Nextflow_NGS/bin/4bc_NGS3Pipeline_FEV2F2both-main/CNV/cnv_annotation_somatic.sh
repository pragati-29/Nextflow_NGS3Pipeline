cd {{location}}/CNV/

input="list.txt"


while IFS= read -r line
do
echo "Starting ${line}"
mkdir ${line}
#preparing config file
echo "##########Starting preparing config file#################"
perl cnv_config_somatic.pl {{location}}/basespace/Projects/{{project_name}}/AppResults/${line}/Files/${line}.bam /home/ubuntu/Programs/NGS3Pipeline/FEV2F2both/CNV/TarGT_First_v2_CDS_GRCh37_13_Mar_23.bed ${line}
echo "##########Ending preparing config file#################"
#run CNV
echo "##########Starting CNV Control Freec#################"
/home/ubuntu/Programs/FREEC-11.6/src/freec -conf ${line}/config_CNV.txt
echo "##########Ending CNV Control Freec#################"
#Annotating file
echo "##########Starting annotation#################"

cd ${line}

cp /Path/bam_ratio_cna_FEV2F2both_V3.py .
python3 bam_ratio_cna_FEV2F2both_V3.py

mkdir MS_Cov
cp /path/AmpliZ_cov_V3.py .
echo "Running AmpliZ_cov_V3.py with arguments: ${line} {{location}}/basespace/Projects/{{project_name}}"
#python3 AmpliZ_cov_V3.py ${line} ${basespace_Path}
python3 AmpliZ_cov_V3.py "${line}" "{{location}}/basespace/Projects/{{project_name}}"

cd ..

#find -type f -name "*_R_cnv_combined.txt" -exec mv {} ./ \;

find -type f -name "*_stat_cntf_cnv_combined.txt" -exec cp {} ./ \;

echo "##########Ending annotation#################"
done < "$input"
echo "################## ALL FILES ARE DONE ###########################"
