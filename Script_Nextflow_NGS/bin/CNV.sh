#!/usr/bin/env bash

# Ensure correct number of arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <location> <csv_file>"
    exit 1
fi

# Assign input arguments to variables
location=$1
csv_file=$2
cnv_dir="$location/cnv"

# Create directory if it doesn't exist
mkdir -p "$cnv_dir"

# Extract 15th (Sample ID) and 5th (Project Name) columns correctly using AWK
awk -F',' 'BEGIN {OFS=","} {if (NR>1) print $(NF-2),$4}' "$csv_file" > "$cnv_dir/list.txt"

input="$cnv_dir/list.txt"
cd "$cnv_dir" || exit 1

# Loop through each line in the extracted list
while IFS=',' read -r sample_id project_name; do
    echo "Processing Sample: ${sample_id}, Project: ${project_name}"
    
    # Debugging print
    echo "Expected Path: $location/basespace/Projects/${project_name}/AppResults/${sample_id}/Files/${sample_id}.bam"
    
    mkdir -p "${sample_id}"
    
    echo "########## Starting preparing config file #################"
    perl /home/bioinfoa/Pragati/Nextflow_NGS3Pipeline/Script_Nextflow_NGS/bin/cnv_config_somatic.pl \
        $location/basespace/Projects/${project_name}/AppResults/${sample_id}/Files/${sample_id}.bam \
        /home/bioinfoa/Programs/NGS3pipeline/FEV2F2both/CNV/TarGT_First_v2_CDS_GRCh37_13_Mar_23.bed \
        ${sample_id}
    echo "########## Ending preparing config file #################"
    
    echo "########## Starting CNV Control Freec #################"
    /home/bioinfoa/Programs/FREEC-11.6/src/freec -conf ${sample_id}/config_CNV.txt
    echo "########## Ending CNV Control Freec #################"
    
    echo "########## Starting annotation #################"
    /home/bioinfoa/Programs/bedtools.static.binary intersect -a ${sample_id}/${sample_id}.bam_CNVs \
        -b /home/bioinfoa/Programs/NGS3pipeline/FEV2F2both/CNV/FE_V2_CDS.bed -loj | \
        sort -V | awk -F"\t" '{print $1"\t"$2"\t"$3"\t"$4"\t"$5"\t"$9}' | \
        awk -vOFS="\t" '$1=$1; BEGIN { str="Chromosome Start End Predicted_copy_number Type_of_alteration Gene"; \
        split(str,arr," "); for(i in arr) printf("%s\t", arr[i]); print}' | \
        awk '$6 != "."' > ./${sample_id}_cnv_combined.txt
    
    echo "########## Ending annotation #################"
done < "$input"

echo "################## ALL FILES ARE DONE ###########################"

