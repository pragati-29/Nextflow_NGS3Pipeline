
#--------Fuseq---Installation--script-------------------------------------------------------------------------------#

# download FuSeq_WES_v1.0.0
wget https://github.com/nghiavtr/FuSeq_WES/releases/download/v1.0.0/FuSeq_WES_v1.0.0.tar.gz -O FuSeq_WES_v1.0.0.tar.gz
tar -xzvf FuSeq_WES_v1.0.0.tar.gz

#configure FuSeq_WES
cd FuSeq_WES_v1.0.0
bash configure.sh
cd ..

# download test data
wget https://www.meb.ki.se/sites/biostatwiki/wp-content/uploads/sites/4/2022/04/FuSeq_WES_testdata.tar.gz
tar -xzvf FuSeq_WES_testdata.tar.gz

# download reference 
wget https://www.meb.ki.se/sites/biostatwiki/wp-content/uploads/sites/4/2022/04/UCSC_hg19_wes_contigSize3000_bigLen130000_r100.tar.gz
tar -xzvf UCSC_hg19_wes_contigSize3000_bigLen130000_r100.tar.gz

#--------Fuseq---Installation--script-------------------------------------------------------------------------------#





echo "##--------------------------------INITIALIZING--DEMO--RUN-----------------------------------------------------------#"

##--------------------------------INITIALIZING--DEMO--RUN-----------------------------------------------------------#
bamfile="FuSeq_WES_testdata/test.bam"
ref_json="UCSC_hg19_wes_contigSize3000_bigLen130000_r100/UCSC_hg19_wes_contigSize3000_bigLen130000_r100.json"
gtfSqlite="UCSC_hg19_wes_contigSize3000_bigLen130000_r100/UCSC_hg19_wes_contigSize3000_bigLen130000_r100.sqlite"
output_dir="test_out"
mkdir $output_dir
python3 FuSeq_WES_v1.0.0/fuseq_wes.py --bam $bamfile  --gtf $ref_json --mapq-filter --outdir $output_dir
fusiondbFn="FuSeq_WES_v1.0.0/Data/Mitelman_fusiondb.RData"
paralogdb="FuSeq_WES_v1.0.0/Data/ensmbl_paralogs_grch37.RData"
Rscript FuSeq_WES_v1.0.0/process_fuseq_wes.R in=$output_dir sqlite=$gtfSqlite fusiondb=$fusiondbFn paralogdb=$paralogdbFn out=$output_dir
##--------------------------------INITIALIZING--DEMO--RUN-----------------------------------------------------------#

