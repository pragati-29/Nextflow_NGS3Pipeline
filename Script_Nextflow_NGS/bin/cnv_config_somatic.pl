#!/usr/bin/perl
use strict;
use warnings;

# Read arguments
my ($path, $bed_file, $output, $chrLenFile, $chrFiles, $sambamba) = @ARGV;

print $bed_file;
print $chrFiles;
# Check arguments
die "Usage: $0 <bam_path> <bed_file> <output_dir> <chrLenFile> <chrFiles> <sambamba>\n" unless @ARGV == 6;

# Open config file for writing
open(my $O, '>', "$output/config_CNV.txt") or die "Cannot open $output/config_CNV.txt: $!";
print $O <<EOF;
[general]
chrLenFile = $chrLenFile
chrFiles = $chrFiles
window = 0
ploidy = 2
intercept = 1
minMappabilityPerWindow = 0.7
outputDir = $output
sex = XY
breakPointType = 2
degree = 3
coefficientOfVariation = 0.05
breakPointThreshold = 0.6
maxThreads = 10
sambamba = $sambamba
SambambaThreads = 10
noisyData = TRUE
printNA = FALSE

[sample]
mateFile = $path
inputFormat = BAM
mateOrientation = FR

[BAF]
minimalCoveragePerPosition = 5

[target]
captureRegions = $bed_file
EOF

close($O);
