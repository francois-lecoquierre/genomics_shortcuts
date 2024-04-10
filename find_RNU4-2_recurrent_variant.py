

# find_RNU4-2_recurrent_variant.py [-bam <path to bam file> | -bam_list <path to bam file list>] -genome <genome version> -output_prefix <output prefix>
# require an unix OS with bcftools to run the mpileup

import argparse
import os
import sys
import subprocess

helper = "find_RNU4-2_recurrent_variant.py [-bam <path to bam file> | -bam_list <path to bam file list>] -genome <genome version> -output_prefix <output prefix>"

def parse_args():
    parser = argparse.ArgumentParser(description='Detect a specific variant in a bam file')
    parser.add_argument('-bam', type=str, help='Path to the bam file')
    parser.add_argument('-bam_list', type=str, help='Path to the bam file list')
    parser.add_argument('-genome', type=str, help='Genome version: hg19 or hg38')
    parser.add_argument('-output_prefix', type=str, help='Output prefix')
    args = parser.parse_args()
    return args


def check_args(args):
    if not args.bam and not args.bam_list:
        print('Error: bam or bam_list is required')
        print(helper)
        sys.exit(1)
    if args.bam and args.bam_list:
        print('Error: only one of bam or bam_list is required')
        print(helper)
        sys.exit(1)
    if not args.genome:
        print('Error: genome is required : hg19 or hg38')
        print(helper)
        sys.exit(1)


def get_chr12_from_bam(bam_file):
    # we chec in the header if chr12 is noted as chr12 or 12
    header = subprocess.check_output(['samtools', 'view', '-H', bam_file]).decode('utf-8')
    if 'chr12' in header:
        return 'chr12'
    elif '12' in header:
        return '12'
    else:
        print('Error: chr12 not found in the header of the bam file : {}'.format(bam_file))

def get_position(genome):
    if genome == 'hg19':
        return '120729642'
    elif genome == 'hg38':
        return '120291839'
    else:
        print('Error: genome version not supported')
        sys.exit(1)


class sample:
    def __init__(self, chr, pos, bam_file):
        self.chr = chr
        self.pos = pos
        self.bam_file = bam_file
        self.count = None
        self.bases = None
        self.qual = None
        self.has_coverage = None
        self.carrier = None
        self.get_mpileup()
        self.get_carrier_status()

    def get_mpileup(self):
        command=['samtools', 'mpileup', '-r', '{}:{}-{}'.format(self.chr, self.pos, self.pos), self.bam_file]
        try:
            output = subprocess.check_output(command).decode('utf-8')
        except subprocess.CalledProcessError:
            print('Error: samtools mpileup failed for {}'.format(self.bam_file))
            self.has_coverage = False
            return
        if not output:
            self.has_coverage = False
            return
        else:
            self.has_coverage = True
        output = output.split('\t')
        try:
            self.count = output[3]
            self.bases = output[4]
            self.qual = output[5].strip()
        except IndexError:
            self.has_coverage = False
            return
    
    def get_carrier_status(self):
        # if the bases contains "+1A" then the sample is a carrier
        if self.bases:
            if '+1A' in self.bases:
                self.carrier = True
            else:
                self.carrier = False



###############################################

args = parse_args()
check_args(args)
if args.bam:
    bam_files = [args.bam]
else:
    with open(args.bam_list) as f:
        bam_files = f.read().splitlines()

genome = args.genome
output_prefix = args.output_prefix
chr12 = get_chr12_from_bam(bam_files[0])
position = get_position(genome)

samples = []
for bam_file in bam_files:
    samples.append(sample(chr12, position, bam_file))

if output_prefix:
    output_file = '{}_RNU4-2_recurrent_variant.tsv'.format(output_prefix)
else:
    output_file = 'RNU4-2_recurrent_variant.tsv'
with open(output_file, 'w') as f:
    f.write('Sample\tIs_covered\tIs_carrier\tCount\tBases\tQual\n')
    for sample in samples:
        f.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(sample.bam_file, sample.has_coverage, sample.carrier, sample.count, sample.bases, sample.qual))

print('Output written to {}'.format(output_file))

    
