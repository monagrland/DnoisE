#!/usr/bin/env python3

"""
.. codeauthor:: Adrià Antich <adriantich@gmail.com>

This programme is called by the DnoisE.

write_ouput.py is designed to export denoised data from DnoisE to fasta or csv files

"""

import multiprocessing as mp
from tqdm import tqdm
import pandas as pd


def write_output(de):
    print('writing output_info')
    if de.entropy:
        de.MOTUoutfile = str(de.MOTUoutfile + '_Adcorr')

    if (de.output_type == 'ratio') or (de.output_type == 'all'):

        if de.output_file_type == 'fasta':
            de.denoised_ratio = de.denoised_ratio.to_dict(orient='index')
            ofile = open(str(de.MOTUoutfile + '_denoised_ratio.fasta'), "w")
            for i in tqdm(range(len(de.denoised_ratio))):
                ofile.write(">" + de.denoised_ratio[i]['id'] + ';size=' + str(de.denoised_ratio[i][de.count]) +
                            ";\n" + de.denoised_ratio[i][de.seq].upper() + "\n")
            # do not forget to close it
            ofile.close()
        elif de.output_file_type == 'csv':
            de.denoised_ratio.to_csv(str(de.MOTUoutfile + '_denoised_ratio.csv'), index=False)

        del de.denoised_ratio

    if (de.output_type == 'd') or (de.output_type == 'all'):

        if de.output_file_type == 'fasta':
            de.denoised_d = de.denoised_d.to_dict(orient='index')
            ofile = open(str(de.MOTUoutfile + '_denoised_d.fasta'), "w")
            for i in tqdm(range(len(de.denoised_d))):
                ofile.write(">" + de.denoised_d[i]['id'] + ';size=' + str(de.denoised_d[i][de.count]) + ";\n" +
                            de.denoised_d[i][de.seq].upper() + "\n")
            # do not forget to close it
            ofile.close()
        elif de.output_file_type == 'csv':
            de.denoised_d.to_csv(str(de.MOTUoutfile + '_denoised_d.csv'), index=False)

        del de.denoised_d

    if (de.output_type == 'ratio_d') or (de.output_type == 'all'):

        if de.output_file_type == 'fasta':
            de.denoised_ratio_d = de.denoised_ratio_d.to_dict(orient='index')
            ofile = open(str(de.MOTUoutfile + '_denoised_ratio_d.fasta'), "w")
            for i in tqdm(range(len(de.denoised_ratio_d))):
                ofile.write(">" + de.denoised_ratio_d[i]['id'] + ';size=' + str(de.denoised_ratio_d[i][de.count]) + ";\n" +
                            de.denoised_ratio_d[i][de.seq].upper() + "\n")
            # do not forget to close it
            ofile.close()
        elif de.output_file_type == 'csv':
            de.denoised_ratio_d.to_csv(str(de.MOTUoutfile + '_denoised_ratio_d.csv'), index=False)

        del de.denoised_ratio_d

