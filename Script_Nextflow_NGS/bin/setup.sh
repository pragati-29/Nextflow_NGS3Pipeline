#!/bin/bash

# Ensure the script runs from the repo root
cd "$(dirname "$0")"

# Define base directory
BIN_DIR="/home/bioinfo/Nilesh/NGS3_test/Downstream_Upstream_Test/Downstream_pipeline/Script_Nextflow_NGS/bin"

# Grant execute permission to all Python files in bin/
chmod +x "$BIN_DIR"/*

# Fix line endings for Python scripts in bin/
find "$BIN_DIR" -name "*.py" -exec sed -i 's/\r$//' {} \;

echo "Setup complete! Python scripts in bin/ are now executable."

export FREEC_PATH="/home/bioinfo/Programs_Assets/FREEC-11.6/src/freec"
export BEDTOOLS_PATH="/home/bioinfo/Programs_Assets/bedtools.static.binary"
export BED_FILE_Fev2_CDS="/home/bioinfoa/Programs/NGS3pipeline/FEV2F2both/CNV/FE_V2_CDS.bed"
export cnv_config="/home/bioinfo/Nilesh/NGS3_test/Nextflow_Downstream/Script_Nextflow_NGS/bin/cnv_config_somatic.pl"
export chrLenFile="/home/bioinfo/Nilesh/NGS3_test/Nextflow_Downstream/Script_Nextflow_NGS/bin/4bc_NGS3Pipeline_FEV2F2both-main/CNV/my_genome.fa.fai"
export chrFiles="/home/bioinfo/Programs_Assets/files_for_control_freec/chromFa"
export sambamba="/home/bioinfo/miniconda3/bin/sambamba"
export COMMON_FILE_DIR="/home/bioinfo/Programs_Assets/files_for_control_freec/Common_files/"
export python_bam_ratio="$BIN_DIR/bam_ratio_cna_FEV2F2both_V3.py"
export Ambiliz="$BIN_DIR/AmpliZ_cov_V3.py"
export Ambiliz_folder="$BIN_DIR/4bc_NGS3Pipeline_FEV2F2both-main/AmpliZ_COV"
export CE_gene_list="$BIN_DIR/gene_list_CE.txt"
export bam_ratio_CE="$BIN_DIR/bam_ratio_cna_CE_V4.py"
export mosdepth="/home/bioinfo/miniconda3/envs/nf_ngs3pipeline_env/bin/mosdepth"
export FREEBAYES_PATH="/home/bioinfo/miniconda3/envs/nf_ngs3pipeline_env/bin/freebayes"
export IGV="home/bioinfoa/Programs/IGV_Linux_2.9.2_WithJava/IGV_Linux_2.9.2/igv"
export fuseq="$BIN_DIR/FuSeq_WES_v1.0.0"
