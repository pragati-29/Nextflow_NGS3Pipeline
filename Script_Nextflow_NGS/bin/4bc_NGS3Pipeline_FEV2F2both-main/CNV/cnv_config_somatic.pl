$path  = $ARGV[0]; $bed_file = $ARGV[1]; $output = $ARGV[2]; 
open (O, ">$output/config_CNV.txt");
print O "[general]

chrLenFile = {{chrLenFile}}
chrFiles = {{chrFiles}}
window = 0
ploidy = 2
intercept=1
minMappabilityPerWindow = 0.7
outputDir = $output
sex=XY
breakPointType=2
degree=3
coefficientOfVariation = 0.05
breakPointThreshold = 0.6
maxThreads = 10
sambamba = {{sambamba}}
SambambaThreads = 10


noisyData = TRUE
printNA=TRUE

[sample]

mateFile = $path
inputFormat = BAM
mateOrientation = FR

[BAF]

minimalCoveragePerPosition = 5

[target]

captureRegions = $bed_file";
