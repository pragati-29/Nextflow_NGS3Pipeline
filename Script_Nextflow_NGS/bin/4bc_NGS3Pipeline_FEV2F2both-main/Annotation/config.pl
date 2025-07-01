$path  = $ARGV[0];
open (O, ">config.ini");
print O "
[CancerVar]
buildver = hg19
# hg19
inputfile = $path.avinput
# the inputfile and the path  BRAF/test.av hg19_clinvar_20151201.avinput
# tab-delimited will be better for including the other information
inputfile_type = AVinput
# the input file type VCF(vcf file with single sample) AVinput VCF_m(vcf file with multiple samples)
outfile = $path.cancervar
# the output file location and prefix of output file
database_cancervar = path/Annotation_db/cancervardb
# the database location/dir for Intervar
lof_genes = %(database_cancervar)s/LOF.genes.exac_me_cancers
mim2gene = %(database_cancervar)s/mim2gene.txt
mim_pheno = %(database_cancervar)s/mim_pheno.txt
mim_orpha = %(database_cancervar)s/mim_orpha.txt
orpha = %(database_cancervar)s/orpha.txt
knowngenecanonical = %(database_cancervar)s/knownGeneCanonical.txt
exclude_snps = %(database_cancervar)s/ext.variants
cancervar_markers=%(database_cancervar)s/cancervar.out.txt
cancer_pathway=%(database_cancervar)s/cancers_genes.list_kegg.txt
cancers_genes=%(database_cancervar)s/cancer_census.genes
cancers_types=%(database_cancervar)s/cancervar.cancer.types
evidence_file = None
# add your own Evidence file for each Variant:
# evidence file as tab-delimited format like this:
# Chr Pos Ref_allele Alt_allele  Evidence_list]
disorder_cutoff = 0.01
#Allele frequency is greater than expected for disorder
[CancerVar_Bool]
onetranscript = FALSE
# TRUE or FALSE: print out only one transcript for exonic variants (default: FALSE/all transcripts)
otherinfo = TRUE
# TRUE or FALSE: print out otherinfo (infomration in fifth column in queryfile default: TRUE)
# We want use the fifth column to provide the cancer types 
# this option only perform well with AVinput file and the other information only can be put in the fifth column.  The information in >5th column will be lost.
# When input as  VCF or VCF_m files with otherinfo option  only het/hom will be kept  depth and qual will be lost  the cancer type should be provide by command option.
[Annovar]
convert2annovar = path/Annotation_db/convert2annovar.pl
#convert input file to annovar format
table_annovar = path/Annotation_db/table_annovar.pl
#
annotate_variation=  path/Annotation_db/annotate_variation.pl
#
database_locat = path/Annotation_db/humandb
# the database location/dir from annnovar   check if database file exists
database_names = ensGene avsnp150 clinvar_20190305 icgc21 introgen cadd13gt20 esp6500siv2_all exac03 gnomad211_exome 1000g2015aug_all 1000g2015aug_SAS dbnsfp35a dbscsnv11 dbnsfp31a_interpro rmsk
# specify the database_names from ANNOVAR or UCSC
[Other]
current_version = CancerVar_20200119
# pipeline version
public_dev = https://github.com/WGLab/CancerVar/releases";

