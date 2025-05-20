#!/bin/bash

# Ensure the script runs from the repo root
cd "$(dirname "$0")"

# Ensure bin/ exists
mkdir -p bin

# Grant execute permission to all Python files in bin/
chmod +x /home/bioinfoa/Pragati/Nextflow_NGS3Pipeline/Script_Nextflow_NGS/bin/*.py #chmod +x *

# Fix line endings for Python scripts in bin/
sed -i 's/\r$//' /home/bioinfoa/Pragati/Nextflow_NGS3Pipeline/Script_Nextflow_NGS/bin/*.py 2>/dev/null || true

echo "Setup complete! Python scripts in bin/ are now executable."

export FREEC_PATH="/home/bioinfoa/Programs/FREEC-11.6/src/freec"
export BEDTOOLS_PATH="/home/bioinfoa/Programs/bedtools.static.binary"
export BED_FILE_Fev2_CDS="/home/bioinfoa/Programs/NGS3pipeline/FEV2F2both/CNV/FE_V2_CDS.bed"
export cnv_config="/home/bioinfoa/Pragati/Nextflow_NGS3Pipeline/Script_Nextflow_NGS/bin/cnv_config_somatic.pl"
export chrLenFile="/home/bioinfoa/Programs/NGS3pipeline/FEV2F2both/CNV/my_genome.fa.fai"
export chrFiles="home/bioinfoa/Programs/files_for_control_freec/chromFa"
export sambamba="/usr/bin/sambamba"
export COMMON_FILE_DIR="/home/bioinfoa/Programs/Freebayes_Test_Runs/Common_files/"
export FREEBAYES_PATH="/usr/bin/freebayes"
export IGV="home/bioinfoa/Programs/IGV_Linux_2.9.2_WithJava/IGV_Linux_2.9.2/igv"
