params.refgenome = "/media/bioinfoa/bioinfo2/Pragati/Lung_annotation/AWS_First/FQ/ref"
params.outdir = "/media/bioinfoa/bioinfo2/Pragati/Lung_annotation/AWS_First/NextF/gatk_results"
params.inputdir = "/media/bioinfoa/bioinfo2/Pragati/Lung_annotation/AWS_First/NextF/*_{R1,R2}.fastq.gz"
params.input_fastq ="/media/bioinfoa/bioinfo2/Pragati/Lung_annotation/AWS_First/NextF"
params.sam_results = "/media/bioinfoa/bioinfo2/Pragati/Lung_annotation/AWS_First/NextF/sam_results"
params.genome_reference_dict = "/media/bioinfoa/bioinfo2/Pragati/Lung_annotation/AWS_First/NextF/ref/hg19.dict"
params.calling_intervals = "/media/bioinfoa/bioinfo2/Pragati/Lung_annotation/AWS_First/NextF/TFirsrt_cds_fus_target_intervals.list"
params.genome_reference_index = "/media/bioinfoa/bioinfo2/Pragati/Lung_annotation/AWS_First/NextF/ref/hg19.fa.fai"
//bam_in.view()
params.bam_results = "/media/bioinfoa/bioinfo2/Pragati/Lung_annotation/AWS_First/NextF/bam_results"
params.cohort_name = "family_trio"
params.vcf_file = "/media/bioinfoa/bioinfo2/Pragati/Lung_annotation/AWS_First/NextF/known_sites.hard-filtered_panel.vcf"
params.dedup_file = "/media/bioinfoa/bioinfo2/Pragati/Lung_annotation/AWS_First/NextF/gatk_results/dedup_result"
log.info"""\
refgenome: ${params.refgenome}/hg19.fa
outdir: ${params.outdir}
inputdir: ${params.inputdir}
"""

process FASTQC {
    container 'biocontainers/fastqc:v0.11.9_cv7'
    tag "FASTQC on $sample_id"

    input:
    tuple val(sample_id), path(inputdir)

    output:
    path "fastqc_${sample_id}_logs"

    script:
    """
    mkdir fastqc_${sample_id}_logs
    fastqc -o fastqc_${sample_id}_logs -f fastq -q ${inputdir}
    """
}

process MULTIQC {
    container 'hydragenetics/multiqc:1.11'
    publishDir params.outdir, mode:'copy'

    input:
    path '*'

    output:
    path 'multiqc_report.html'

    script:
    """
    multiqc .
    """
}


process alignment {
  container 'biocontainers/bwa:v0.7.15_cv4' 
  publishDir "${params.outdir}/alignment_results", mode: "copy"

  tag "Alignment on $sample_id"

  input:
    path "${params.refgenome}"
    tuple val(sample_id), path(reads)
  output:
    path "${sample_id}.sam"

  script:
    """
    bwa mem -P "${params.refgenome}"/hg19 ${reads[0]} ${reads[1]} > ${sample_id}.sam
    """
}
process sam_to_bam {
  container "biocontainers/samtools:v1.3.1_cv4"
  publishDir params.bam_results, mode: "copy"
  tag "bam_sam on $sample_id"
  input:
    path bam_in
  output:
    path "${bam_in.baseName}.bam"
  script:
    """
    mkdir -p bam_results
    samtools view -S -b ${bam_in} > ${bam_in.baseName}.bam
    samtools sort ${bam_in.baseName}.bam > ${bam_in.baseName}.bam
    """
}
process SAMTOOLS_INDEX {
    container 'quay.io/biocontainers/samtools:1.19.2--h50ea8bc_1' 

    input:
      path bam_ch

    output:
      path "${bam_ch}.bai"

    script:
    """
    samtools index '${bam_ch}'
    """
}
process fasta_to_dict{
  container 'quay.io/biocontainers/samtools:1.19.2--h50ea8bc_1'
  publishDir params.refgenome, mode: "copy"
  input:
    path refgenome
  output:
    path "hg19.dict"
  script:
    """
    samtools dict ${refgenome}/hg19.fa --output hg19.dict
    """
}
process markdups {
  container "broadinstitute/gatk:4.5.0.0"
  publishDir params.outdir, mode: "copy"

  input:
    path bam_results

  output:
    path 'dedup_result'
  
  script:
    """
    mkdir dedup_result
    gatk MarkDuplicates -I ${bam_results} -O sorted_dedup_${bam_results} -M sorted_dedup_metrics_${bam_results.baseName}.txt
    samtools index sorted_dedup_${bam_results}
    mv sorted_dedup_* ./dedup_result
    """
}
process readgroups {
  container "broadinstitute/gatk:4.5.0.0"
  publishDir params.outdir, mode: "copy"

  input:
    path dedup_result
    path vcf_file
  output:
    path 'dedup_result'

  script:
    """
    gatk AddOrReplaceReadGroups -I ${dedup_result}/*.bam -O rg_sorted_dedup.bam -LB readgroup -PL illumina -PU ESWJFHU537GDFJK -SM Sample-4BC
    gatk IndexFeatureFile --input ${params.vcf_file} > dedup_result/known_sites.hard-filtered_panel.vcf
    mv rg_sorted_dedup.bam ./dedup_result
    """

}
process baserecal {
    container "broadinstitute/gatk:4.5.0.0"
    publishDir "${params.outdir}/recal_report", mode: "copy"

    input:
        path refs
        path dedup_result
        path vcf_file
    output:
        path 'recal_report.table'
    script:
        """
        gatk BaseRecalibrator -R ${params.refgenome}/hg19.fa -I ${dedup_result}/rg_sorted_dedup.bam --known-sites ${params.vcf_file} -O recal_report.table
        """
}
/*process apply_bqsr {

  publishDir params.outdir, mode:"copy"

  input:
    path bwa_indexes
    path dedup_result
    path recal_report

  output:
    path 'recal_report'

  script:
    """
    gatk ApplyBQSR -R $bwa_indexes/chr7.fa -I $dedup_result/rg_sorted_dedup_${params.sampleid}.bam --bqsr-recal-file $recal_report/recal_report_${params.sampleid}.table -O recalibrated_${params.sampleid}.bam
    mv recalibrated_* ./recal_report
    """
}
process haplo {

  publishDir params.outdir, mode:"copy"

  input:
    path bwa_indexes
    path recal_report
  
  output:
    path 'variant_file'

  script:
    """
    mkdir variant_file
    gatk HaplotypeCaller -R $bwa_indexes/chr7.fa -I $recal_report/recalibrated_${params.sampleid}.bam -O variants_${params.sampleid}.vcf
    mv variants_* ./variant_file
    """
}*/
workflow {
    Channel
        .fromFilePairs(params.inputdir, checkIfExists: true)
        .set { read_pairs_ch }

  //read_pairs_ch.view()  
  //fastqc_ch = FASTQC(read_pairs_ch)
  //MULTIQC((fastqc_ch).collect())
  //bwa_index_files = indexing("${params.refgenome}")
  //alignment("${params.refgenome}", read_pairs_ch)
  //sorted_bam_file.collect().view()
  //bam_ch = sam_to_bam(alignment.out)
  //samindex_ch = SAMTOOLS_INDEX(bam_ch)
  //fasta_to_dict(params.refgenome)
  //dedup_file = markdups(bam_ch)
  //dedup_file.view()
  //rg_sorted_file = readgroups(markdups.out, params.vcf_file)
  recalibration_report = baserecal("${params.refgenome}",params.dedup_file, params.vcf_file)
  //recalibrated_bam_file = apply_bqsr(bwa_index_files, rg_sorted_file, recalibration_report)
  //haplo(bwa_index_files, recalibrated_bam_file)
}
