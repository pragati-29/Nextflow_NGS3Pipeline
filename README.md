# Nextflow_NGS3Pipelin 
## Aim:- Implementation of NGS3Pipeline in Nextflow 
## Overview 
This script defines a Nextflow pipeline used for processing and uploading sequencing data. It handles renaming files and uploading datasets to BaseSpace projects based on specific sample naming conventions. The workflow is structured around parameter definitions, individual processes, and a workflow definition. 
## 1. Parameter Definitions 
  ### Parameters in Nextflow scripts provide configurable values that can be adjusted without modifying the core script logic. 
  params.input_dir = "/home/pragati_4bc/NGS3Pipeline_Nextflow/sample" 
  params.reads = "/home/pragati_4bc/NGS3Pipeline_Nextflow/sample/*_{R1_001,R2_001}.fastq.gz" 
  params.output_dir = "/home/pragati_4bc/NGS3Pipeline_Nextflow/Output" 
  params.project_id_DNA_somatic = "" // Placeholder for somatic project ID 
  params.project_id_DNA_Germline = "" // Placeholder for germline project ID 
  params.project_id_RNA = "" // Placeholder for RNA project ID 
### Purpose of Parameters: 
    params.input_dir: Specifies the directory containing input files. 
    params.reads: Matches paired-end FASTQ files based on a naming pattern (e.g., *_R1_001.fastq.gz and *_R2_001.fastq.gz). 
    params.output_dir: Directory for pipeline outputs. 
    params.project_id_DNA_somatic, params.project_id_DNA_Germline, params.project_id_RNA: Placeholder IDs for BaseSpace projects for different sample types. 
    params.sam_pattern: List of substrings used to classify samples. 
## 2. Process Definitions 
    Processes in Nextflow are isolated units of computation. Each process defines its inputs, outputs, and a script to execute. 
    process Renaming {
    script:
    """python3 /media/bioinfoa/bioinfo2/Pragati/NGS3Pipeline_Nextflow/Rename_combined.py "${params.input_dir}"
    """
    }
    
    
