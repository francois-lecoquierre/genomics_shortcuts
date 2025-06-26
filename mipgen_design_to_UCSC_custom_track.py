#!/usr/bin/env python


"""
Creates a UCSC custom track file from a mipgen design file.
"""

import pandas as pd
import os
import numpy as np
import argparse
import sys

# === Description ===
parser = argparse.ArgumentParser(
    description="Reformat MIPGEN design file (.picked_mips.txt) into UCSC custom track file."
)

# === Arguments ===
parser.add_argument(
    "--input-file",
    type=str,
    required=True,
    help="Input MIPGEN design file (.picked_mips.txt). Required."
)
parser.add_argument(
    "--color-by-logistic-score",
    action="store_true",
    help="Use the logistic score to color the tracks. If set, overrides --color. Default: False."
)
parser.add_argument(
    "--output-file",
    type=str,
    default="mipgen_custom_track.bed",
    help="Output file name for the UCSC custom track. Default: mipgen_custom_track.bed."
)
parser.add_argument(
    "--color",
    type=str,
    default="17,122,101",
    help="Color for the tracks in RGB format (e.g., 125,0,255). Ignored if --color-by-logistic-score is set."
)

# === Parse arguments ===
args = parser.parse_args()

# === Validation ===
if not os.path.isfile(args.input_file):
    print(f"Error: Input file '{args.input_file}' does not exist.", file=sys.stderr)
    exit(1)


# Create a dataframe
df = pd.read_csv(args.input_file, sep="\t", header=0, low_memory=False)
# Enrich with output custom track columns
df['start'] = np.where(df['probe_strand'] == '+', df['ext_probe_start'], df['lig_probe_start'])
df['end'] = np.where(df['probe_strand'] == '+', df['lig_probe_stop'], df['ext_probe_stop'])
df['name'] = df['mip_name']
# Logistic score varies from 0 to 1, scores varies from 0 to 1000
df['score'] = np.where(args.color_by_logistic_score, (df['logistic_score'] * 1000).astype(int), 0)
df['strand'] = df['probe_strand']
df['thickstart'] = np.where(df['probe_strand'] == '+', df['ext_probe_start'], df['lig_probe_start'])
df['thickend'] = np.where(df['probe_strand'] == '+', df['lig_probe_stop'], df['ext_probe_stop'])
df['color'] = args.color
df['blockcount'] = "3"
df['blocksizes'] = np.where(df['probe_strand'] == '+', (df['ext_probe_stop'] - df['ext_probe_start']).astype(str) + "," + (df['feature_stop_position'] - df['feature_start_position']).astype(str) + ',' + (df['lig_probe_stop'] - df['lig_probe_start']).astype(str), (df['lig_probe_stop'] - df['lig_probe_start']).astype(str) + "," + (df['feature_stop_position'] - df['feature_start_position']).astype(str) + ',' + (df['ext_probe_stop'] - df['ext_probe_start']).astype(str))
df['blocstarts'] = np.where(df['probe_strand'] == '+', "0," + (df['feature_start_position']-df['ext_probe_start']).astype(str) + ',' + (df['lig_probe_start']-df['ext_probe_start']).astype(str), "0," + (df['feature_start_position']-df['lig_probe_start']).astype(str) + ',' + (df['ext_probe_start']-df['lig_probe_start']).astype(str))
# Extract cols for UCSC custom track file
df_out = (df[['chr', 'start', 'end', 'name', 'score', 'strand', 'thickstart', 'thickend', 'color', 'blockcount', 'blocksizes', 'blocstarts']])


# Create the header line for the UCSC custom track file
experiment_name = os.path.basename(args.input_file).removesuffix('.picked_mips.txt')
if args.color_by_logistic_score:
    usescore_suffix =  " useScore=1"
    header_line = f"track name='MIPGEN design {experiment_name}' description='MIPGEN design {experiment_name} - color by MIPGEN Logistic Score' visibility=3 useScore=1 itemRgb='Off'"
else:
    header_line = f"track name='MIPGEN design {experiment_name}' description='MIPGEN design {experiment_name}' itemRgb='On' visibility=3"


# Write the output to a BED file
output_file = args.output_file
df_out.to_csv(output_file, sep="\t", index=False, header=False)
# Add the header line to the output file
with open(output_file, 'r+') as f:
    content = f.read()
    f.seek(0, 0)  # Move the cursor to the beginning of the file
    f.write(header_line + '\n' + content)  # Write the header line followed by the original content

print(f"Generated UCSC custom track file: {output_file}")

# === End of script ===
