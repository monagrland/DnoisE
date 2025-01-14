#!/usr/bin/env python3

"""
.. codeauthor:: Adrià Antich <adriantich@gmail.com>

This programme is called by the DnoisE.

running_denoise.py runs the algorithm of denoising sequences using Levenshtein distance or entropy correction.

"""

import itertools
import multiprocessing as mp
import numpy as np
import pandas as pd
from tqdm import tqdm
from dnoise.denoise_functions import *
import dnoise.entropy as en


def run_denoise(de, test=False):
    # if not platform.system() == 'Linux':
    #     print('not Linux system detected')
    #     mp.set_start_method('spawn')

    if de.output_type == 'ratio':
        de.denoised_ratio_output = [de.data_initial.loc[0, de.id]]
    else:
        de.denoised_d_output = [de.data_initial.loc[0, de.id]]
        de.denoised_ratio_output = [de.data_initial.loc[0, de.id]]
        de.denoised_ratio_d_output = [de.data_initial.loc[0, de.id]]

    de.output_info = [{'daughter': de.data_initial.loc[0, de.id], 'mother_d': None, 'd': None,
                       'mother_ratio': None, 'ratio': None,
                       'mother_ratio_d': None, 'ratio_d': None}]

    de.good_seq = [True]
    de.abund_col_names.insert(0, de.count)
    de.run_list = [{de.id: de.data_initial.loc[0, de.id], de.count: de.data_initial.loc[0, de.count],
                    'run': True, 'daughter': False}]

    run_dnoise_testing(de)  # function in denoise_functions.py

    de.output_info = pd.DataFrame.from_dict(de.output_info)
    # if not test:
    #     de.output_info.to_csv(str(de.MOTUoutfile + '_denoising_info.csv'), index=False)

    if (de.output_type == 'ratio') or (de.output_type == 'all'):
        mothers_ratio = de.output_info.mother_ratio.unique()[1:]
    if (de.output_type == 'd') or (de.output_type == 'all'):
        mothers_d = de.output_info.mother_d.unique()[1:]
    if (de.output_type == 'ratio_d') or (de.output_type == 'all'):
        mothers_ratio_d = de.output_info.mother_ratio_d.unique()[1:]

    # del de.output_info

    de.data_initial = de.data_initial.set_index(de.data_initial.loc[:, de.id])

    if (de.output_type == 'ratio') or (de.output_type == 'all'):
        de.good_mothers = de.data_initial.loc[de.good_seq][de.first_col_names + de.abund_col_names + [de.seq]]
        print('writing output_ratio')
        # writing ratio
        if len(mothers_ratio) == 0:
            de.denoised_ratio = de.good_mothers
            de.denoised_ratio = de.denoised_ratio.sort_values([de.count], axis=0, ascending=False)
        else:
            if de.cores > 1:
                pool = mp.Pool(de.cores)
                [row] = zip(*pool.map(de.write_output_ratio, [mother for mother in mothers_ratio]))
                pool.close()
                del pool
                de.denoised_ratio = pd.DataFrame(row, columns=[de.first_col_names + de.abund_col_names + [de.seq]][0])
                de.good_mothers = de.good_mothers.drop(index=mothers_ratio)
                de.denoised_ratio = pd.concat([de.denoised_ratio, de.good_mothers], ignore_index=True)
                de.denoised_ratio = de.denoised_ratio.sort_values([de.count], axis=0, ascending=False)
            else:
                de.denoised_ratio = pd.DataFrame(columns=[de.first_col_names + de.abund_col_names + [de.seq]][0])
                for mother in tqdm(mothers_ratio):
                    row = [
                        de.good_mothers[list(de.good_mothers.loc[:, de.id] == mother)][
                            de.first_col_names].values.tolist()[
                            0] +
                        list(de.data_initial.loc[
                                 list(pd.Series(de.denoised_ratio_output) == mother), de.abund_col_names].sum(0)) +
                        de.good_mothers[list(de.good_mothers.loc[:, de.id] == mother)][de.seq].values.tolist()]
                    row = pd.Series(row[0], index=[de.first_col_names + de.abund_col_names + [de.seq]][0])
                    row = row.to_frame().T
                    de.denoised_ratio = pd.concat([de.denoised_ratio, row], ignore_index=True)
                    de.good_mothers = de.good_mothers.drop(index=mother)
                de.denoised_ratio = pd.concat([de.denoised_ratio, de.good_mothers], ignore_index=True)
                de.denoised_ratio = de.denoised_ratio.sort_values([de.count], axis=0, ascending=False)
            if 'row' in locals():
                del row
        del de.good_mothers, mothers_ratio, de.denoised_ratio_output

    if (de.output_type == 'd') or (de.output_type == 'all'):
        de.good_mothers = de.data_initial.loc[de.good_seq][de.first_col_names + de.abund_col_names + [de.seq]]
        print('writing output_d')
        # writing d
        if len(mothers_d) == 0:
            de.denoised_d = de.good_mothers
            de.denoised_d = de.denoised_d.sort_values([de.count], axis=0, ascending=False)
        else:
            if de.cores > 1:
                pool = mp.Pool(de.cores)
                [row] = zip(*pool.map(de.write_output_d, [mother for mother in mothers_d]))
                pool.close()
                del pool
                de.denoised_d = pd.DataFrame(row, columns=[de.first_col_names + de.abund_col_names + [de.seq]][0])
                de.good_mothers = de.good_mothers.drop(index=mothers_d)
                de.denoised_d = pd.concat([de.denoised_d, de.good_mothers], ignore_index=True)
                de.denoised_d = de.denoised_d.sort_values([de.count], axis=0, ascending=False)
            else:
                de.denoised_d = pd.DataFrame(columns=[de.first_col_names + de.abund_col_names + [de.seq]][0])
                for mother in tqdm(mothers_d):
                    row = [
                        de.good_mothers[list(de.good_mothers.loc[:, de.id] == mother)][
                            de.first_col_names].values.tolist()[
                            0] +
                        list(de.data_initial.loc[
                            list(pd.Series(de.denoised_d_output) == mother), de.abund_col_names].sum(
                            0)) +
                        de.good_mothers[list(de.good_mothers.loc[:, de.id] == mother)][de.seq].values.tolist()]
                    row = pd.Series(row[0], index=[de.first_col_names + de.abund_col_names + [de.seq]][0])
                    row = row.to_frame().T
                    de.denoised_d = pd.concat([de.denoised_d, row], ignore_index=True)
                    de.good_mothers = de.good_mothers.drop(index=mother)
                de.denoised_d = pd.concat([de.denoised_d, de.good_mothers], ignore_index=True)
                de.denoised_d = de.denoised_d.sort_values([de.count], axis=0, ascending=False)
            if 'row' in locals():
                del row
        del de.good_mothers, mothers_d, de.denoised_d_output

    if (de.output_type == 'ratio_d') or (de.output_type == 'all'):
        de.good_mothers = de.data_initial.loc[de.good_seq][de.first_col_names + de.abund_col_names + [de.seq]]
        print('writing output_ratio_d')
        # writing ratio_d
        if len(mothers_ratio_d) == 0:
            de.denoised_ratio_d = de.good_mothers
            de.denoised_ratio_d = de.denoised_ratio_d.sort_values([de.count], axis=0, ascending=False)
        else:
            if de.cores > 1:
                pool = mp.Pool(de.cores)
                [row] = zip(*pool.map(de.write_output_ratio_d, [mother for mother in mothers_ratio_d]))
                pool.close()
                del pool
                de.denoised_ratio_d = pd.DataFrame(row, columns=[de.first_col_names + de.abund_col_names + [de.seq]][0])
                de.good_mothers = de.good_mothers.drop(index=mothers_ratio_d)
                de.denoised_ratio_d = pd.concat([de.denoised_ratio_d, de.good_mothers], ignore_index=True)
                de.denoised_ratio_d = de.denoised_ratio_d.sort_values([de.count], axis=0, ascending=False)
            else:
                de.denoised_ratio_d = pd.DataFrame(columns=[de.first_col_names + de.abund_col_names + [de.seq]][0])
                for mother in tqdm(mothers_ratio_d):
                    row = [
                        de.good_mothers[list(de.good_mothers.loc[:, de.id] == mother)][de.first_col_names].values.tolist()[
                            0] +
                        list(de.data_initial.loc[
                            list(pd.Series(de.denoised_ratio_d_output) == mother), de.abund_col_names].sum(
                            0)) +
                        de.good_mothers[list(de.good_mothers.loc[:, de.id] == mother)][de.seq].values.tolist()]
                    row = pd.Series(row[0], index=[de.first_col_names + de.abund_col_names + [de.seq]][0])
                    row = row.to_frame().T
                    de.denoised_ratio_d = pd.concat([de.denoised_ratio_d, row], ignore_index=True)
                    de.good_mothers = de.good_mothers.drop(index=mother)
                de.denoised_ratio_d = pd.concat([de.denoised_ratio_d, de.good_mothers], ignore_index=True)
                de.denoised_ratio_d = de.denoised_ratio_d.sort_values([de.count], axis=0, ascending=False)
            if 'row' in locals():
                del row
        del de.good_mothers, mothers_ratio_d, de.denoised_ratio_d_output


def run_denoise_entropy(de):
    # if not platform.system() == 'Linux':
    #     print('not Linux system detected')
    #     mp.set_start_method('spawn')

    print('running data')

    seq_length_per_read = {}
    seq_length = list(map(len, np.array(de.data_initial.loc[:, de.seq])))
    uniq_seq_lengths = set(seq_length)
    uniq_seq_lengths = list(uniq_seq_lengths)

    for i in uniq_seq_lengths:
        count_sum = sum(de.data_initial.loc[(np.asarray(seq_length) == i), de.count])
        seq_length_per_read[i] = count_sum
    max_count_sum = max(list(seq_length_per_read.values()))

    print('seq lengths computed')

    # separate data in different DataFrames by sequence length
    if len(de.modal_length_value) == 0:
        de.modal_length_value = [k for k, v in seq_length_per_read.items() if float(v) == max_count_sum]

    if len(de.modal_length_value) != 1:
        for e in range(0, len(de.modal_length_value)):
            if ((de.modal_length_value[e] - 1) % 3) == 0:
                good_modal_length_value = [de.modal_length_value[e]]
                break
        if 'good_modal_length_value' not in locals():
            good_modal_length_value = [de.modal_length_value[0]]

        print('WARNING!! %s not available to run with entropy correction. '
              'Equal number of seqs with different seq length' % de.MOTUfile)
        print('set -m as one value of the following: %s ' % de.modal_length_value)
        print('DnoisE will run with sequence length %s and its accepted variations (multiples of 3 '
              'nucleotides)' % good_modal_length_value)
    else:
        good_modal_length_value = de.modal_length_value

    if de.unique_length:
        allowed_lengths = good_modal_length_value
    else:
        allowed_lengths = np.array(uniq_seq_lengths) - good_modal_length_value
        allowed_lengths = list(allowed_lengths % 3 == 0)
        allowed_lengths = list(itertools.compress(uniq_seq_lengths, allowed_lengths))
        allowed_lengths.remove(good_modal_length_value[0])
        allowed_lengths.insert(0, good_modal_length_value[0])

    del seq_length_per_read, de.modal_length_value, max_count_sum

    de.output_info = pd.DataFrame()
    if (de.output_type == 'ratio') or (de.output_type == 'all'):
        de.denoised_ratio = pd.DataFrame()
    if (de.output_type == 'd') or (de.output_type == 'all'):
        de.denoised_d = pd.DataFrame()
    if (de.output_type == 'ratio_d') or (de.output_type == 'all'):
        de.denoised_ratio_d = pd.DataFrame()

    for i in list(range(len(allowed_lengths))):
        len_seq = allowed_lengths[i]

        desub = DnoisEFunctions()
        copy_to_subset(declass=de, desub=desub, seq_length=seq_length, len_seq=len_seq)
        seq_length = list(filter(len_seq.__ne__, seq_length))
        if i == 0:
            if de.compute_entropy:
                if desub.initial_pos == 1:
                    e1, e2, e3 = en.mean_entropy(desub.data_initial, de.seq, de.count)
                if desub.initial_pos == 2:
                    e2, e3, e1 = en.mean_entropy(desub.data_initial, de.seq, de.count)
                if desub.initial_pos == 3:
                    e3, e1, e2 = en.mean_entropy(desub.data_initial, de.seq, de.count)
                desub.Ad1 = e1 * 3 / (e1 + e2 + e3)
                de.Ad1 = e1 * 3 / (e1 + e2 + e3)
                desub.Ad2 = e2 * 3 / (e1 + e2 + e3)
                de.Ad2 = e2 * 3 / (e1 + e2 + e3)
                desub.Ad3 = e3 * 3 / (e1 + e2 + e3)
                de.Ad3 = e3 * 3 / (e1 + e2 + e3)
                print('entropy values for length {:.0f} (first nt is a position {:.0f}):\n'
                      '\t {:.3f} for first position of codon\n'
                      '\t {:.3f} for second position of codon\n'
                      '\t {:.3f} for third position of codon'.format(len_seq, desub.initial_pos, e1, e2, e3))

        # maximum ratio allowed
        desub.max_ratio = (1 / 2) ** (desub.alpha * 1 * min(desub.Ad1, desub.Ad2, desub.Ad3) + 1)
        # desub.max_ratio = ((1 / 2) ** (desub.alpha + 1)) * (1 / min(desub.Ad1, desub.Ad2, desub.Ad3))

        if desub.output_type == 'ratio':
            desub.denoised_ratio_output = [desub.data_initial.loc[0, de.id]]
        else:
            desub.denoised_d_output = [desub.data_initial.loc[0, de.id]]
            desub.denoised_ratio_output = [desub.data_initial.loc[0, de.id]]
            desub.denoised_ratio_d_output = [desub.data_initial.loc[0, de.id]]

        desub.output_info = [{'daughter': desub.data_initial.loc[0, de.id], 'mother_d': None, 'd': None,
                              'mother_ratio': None, 'ratio': None,
                              'mother_ratio_d': None, 'ratio_d': None,
                              'difpos1': None, 'difpos2': None, 'difpos3': None,
                              'dtotal': None, 'betacorr': None}]
        desub.good_seq = [True]
        desub.abund_col_names.insert(0, de.count)
        desub.run_list = [{de.id: desub.data_initial.loc[0, de.id], de.count: desub.data_initial.loc[0, de.count],
                           'run': True, 'daughter': False}]

        run_dnoise_testing(desub)

        desub.output_info = pd.DataFrame.from_dict(desub.output_info)

        if (desub.output_type == 'ratio') or (desub.output_type == 'all'):
            mothers_ratio = desub.output_info.mother_ratio.unique()[1:]
        if (desub.output_type == 'd') or (desub.output_type == 'all'):
            mothers_d = desub.output_info.mother_d.unique()[1:]
        if (desub.output_type == 'ratio_d') or (desub.output_type == 'all'):
            mothers_ratio_d = desub.output_info.mother_ratio_d.unique()[1:]

        de.output_info = pd.concat([de.output_info, desub.output_info], ignore_index=True)

        del desub.output_info

        desub.data_initial = desub.data_initial.set_index(desub.data_initial.loc[:, de.id])

        if (desub.output_type == 'ratio') or (desub.output_type == 'all'):
            desub.good_mothers = desub.data_initial.loc[desub.good_seq][de.first_col_names +
                                                                        desub.abund_col_names + [de.seq]]
            # writing ratio
            if len(mothers_ratio) == 0:
                desub.denoised_ratio = desub.good_mothers
                desub.denoised_ratio = desub.denoised_ratio.sort_values([de.count], axis=0, ascending=False)
            else:
                if de.cores > 1:
                    pool = mp.Pool(de.cores)
                    [row] = zip(*pool.map(desub.write_output_ratio, [mother for mother in mothers_ratio]))
                    pool.close()
                    del pool
                    desub.denoised_ratio = pd.DataFrame(row,
                                                        columns=[de.first_col_names + desub.abund_col_names +
                                                                 [de.seq]][0])
                    desub.good_mothers = desub.good_mothers.drop(index=mothers_ratio)
                    desub.denoised_ratio = pd.concat([desub.denoised_ratio, desub.good_mothers], ignore_index=True)
                    desub.denoised_ratio = desub.denoised_ratio.sort_values([desub.count], axis=0, ascending=False)
                else:
                    desub.denoised_ratio = pd.DataFrame(columns=[de.first_col_names + desub.abund_col_names + [de.seq]][0])
                    for mother in tqdm(mothers_ratio):
                        row = [
                            desub.good_mothers[list(desub.good_mothers.loc[:, de.id] == mother)][de.first_col_names
                            ].values.tolist()[0] +
                            list(desub.data_initial.loc[
                                list(pd.Series(desub.denoised_ratio_output) == mother), desub.abund_col_names].sum(
                                0)) +
                            desub.good_mothers[list(desub.good_mothers.loc[:, de.id] == mother)][de.seq].values.tolist()]
                        row = pd.Series(row[0], index=[de.first_col_names + desub.abund_col_names + [de.seq]][0])
                        row = row.to_frame().T
                        desub.denoised_ratio = pd.concat([desub.denoised_ratio, row], ignore_index=True)
                        desub.good_mothers = desub.good_mothers.drop(index=mother)
                    desub.denoised_ratio = pd.concat([desub.denoised_ratio, desub.good_mothers], ignore_index=True)
                    desub.denoised_ratio = desub.denoised_ratio.sort_values([desub.count], axis=0, ascending=False)
                if 'row' in locals():
                    del row
            de.denoised_ratio = pd.concat([de.denoised_ratio, desub.denoised_ratio], ignore_index=True)
            del desub.denoised_ratio, desub.good_mothers, mothers_ratio, desub.denoised_ratio_output

        if (desub.output_type == 'd') or (desub.output_type == 'all'):
            desub.good_mothers = desub.data_initial.loc[desub.good_seq][de.first_col_names +
                                                                        desub.abund_col_names + [de.seq]]
            # writing d
            if len(mothers_d) == 0:
                desub.denoised_d = desub.good_mothers
                desub.denoised_d = desub.denoised_d.sort_values([de.count], axis=0, ascending=False)
            else:
                if de.cores > 1:
                    pool = mp.Pool(de.cores)
                    [row] = zip(*pool.map(desub.write_output_d, [mother for mother in mothers_d]))
                    pool.close()
                    del pool
                    desub.denoised_d = pd.DataFrame(row, columns=[de.first_col_names + desub.abund_col_names + [de.seq]][0])
                    desub.good_mothers = desub.good_mothers.drop(index=mothers_d)
                    desub.denoised_d = pd.concat([desub.denoised_d, desub.good_mothers], ignore_index=True)
                    desub.denoised_d = desub.denoised_d.sort_values([de.count], axis=0, ascending=False)
                else:
                    desub.denoised_d = pd.DataFrame(columns=[de.first_col_names + desub.abund_col_names + [de.seq]][0])
                    for mother in tqdm(mothers_d):
                        row = [
                            desub.good_mothers[list(desub.good_mothers.loc[:, de.id] == mother)][
                                de.first_col_names].values.tolist()[
                                0] +
                            list(desub.data_initial.loc[
                                list(pd.Series(desub.denoised_d_output) == mother), desub.abund_col_names].sum(
                                0)) +
                            desub.good_mothers[list(desub.good_mothers.loc[:, de.id] == mother)][de.seq].values.tolist()]
                        row = pd.Series(row[0], index=[de.first_col_names + desub.abund_col_names + [de.seq]][0])
                        row = row.to_frame().T
                        desub.denoised_d = pd.concat([desub.denoised_d, row], ignore_index=True)
                        desub.good_mothers = desub.good_mothers.drop(index=mother)
                    desub.denoised_d = pd.concat([desub.denoised_d, desub.good_mothers], ignore_index=True)
                    desub.denoised_d = desub.denoised_d.sort_values([desub.count], axis=0, ascending=False)
                if 'row' in locals():
                    del row
            de.denoised_d = pd.concat([de.denoised_d, desub.denoised_d], ignore_index=True)
            del desub.denoised_d, desub.good_mothers, mothers_d, desub.denoised_d_output

        if (desub.output_type == 'ratio_d') or (desub.output_type == 'all'):
            desub.good_mothers = desub.data_initial.loc[desub.good_seq][
                de.first_col_names + desub.abund_col_names + [de.seq]]
            # writing ratio_d
            if len(mothers_ratio_d) == 0:
                desub.denoised_ratio_d = desub.good_mothers
                desub.denoised_ratio_d = desub.denoised_ratio_d.sort_values([de.count], axis=0, ascending=False)
            else:
                if de.cores > 1:
                    pool = mp.Pool(de.cores)
                    [row] = zip(*pool.map(desub.write_output_ratio_d, [mother for mother in mothers_ratio_d]))
                    pool.close()
                    del pool
                    desub.denoised_ratio_d = pd.DataFrame(row,
                                                          columns=[de.first_col_names + desub.abund_col_names + [de.seq]][
                                                              0])
                    desub.good_mothers = desub.good_mothers.drop(index=mothers_ratio_d)
                    desub.denoised_ratio_d = pd.concat([desub.denoised_ratio_d, desub.good_mothers], ignore_index=True)
                    desub.denoised_ratio_d = desub.denoised_ratio_d.sort_values([desub.count], axis=0, ascending=False)
                else:
                    desub.denoised_ratio_d = pd.DataFrame(
                        columns=[de.first_col_names + desub.abund_col_names + [de.seq]][0])
                    for mother in tqdm(mothers_ratio_d):
                        row = [
                            desub.good_mothers[list(desub.good_mothers.loc[:, de.id] == mother)][
                                de.first_col_names].values.tolist()[
                                0] +
                            list(desub.data_initial.loc[
                                list(pd.Series(desub.denoised_ratio_d_output) == mother), desub.abund_col_names].sum(
                                0)) +
                            desub.good_mothers[list(desub.good_mothers.loc[:, de.id] == mother)][de.seq].values.tolist()]
                        row = pd.Series(row[0], index=[de.first_col_names + desub.abund_col_names + [de.seq]][0])
                        row = row.to_frame().T
                        desub.denoised_ratio_d = pd.concat([desub.denoised_ratio_d, row], ignore_index=True)
                        desub.good_mothers = desub.good_mothers.drop(index=mother)
                    desub.denoised_ratio_d = pd.concat([desub.denoised_ratio_d, desub.good_mothers], ignore_index=True)
                    desub.denoised_ratio_d = desub.denoised_ratio_d.sort_values([desub.count], axis=0, ascending=False)
                if 'row' in locals():
                    del row
            de.denoised_ratio_d = pd.concat([de.denoised_ratio_d, desub.denoised_ratio_d], ignore_index=True)
            del desub.denoised_ratio_d, desub.good_mothers, mothers_ratio_d, desub.denoised_ratio_d_output

        del desub

    # de.output_info.to_csv(str(de.MOTUoutfile + '_denoising_info.csv'), index=False)
    # del de.output_info


def run_from_info(de):
    # if not platform.system() == 'Linux':
    #     print('not Linux system detected')
    #     mp.set_start_method('spawn')

    de.data_initial.index = de.data_initial[de.id]
    de.abund_col_names.insert(0, de.count)
    if (de.output_type == 'ratio') or (de.output_type == 'all'):
        mothers_ratio = de.merge_data.mother_ratio.unique()[1:]
        de.good_mothers = de.data_initial.loc[de.merge_data.daughter[de.merge_data.mother_d.isna()]][de.first_col_names +
                                                                                                     de.abund_col_names +
                                                                                                     [de.seq]]
        print('writing output_ratio')
        # writing ratio
        if len(mothers_ratio) == 0:
            de.denoised_ratio = de.good_mothers
            de.denoised_ratio = de.denoised_ratio.sort_values([de.count], axis=0, ascending=False)
        else:
            if de.cores > 1:
                pool = mp.Pool(de.cores)
                [row] = zip(*pool.map(de.write_ratio_from_info, [mother for mother in mothers_ratio]))
                pool.close()
                del pool
                de.denoised_ratio = pd.DataFrame(row, columns=[de.first_col_names + de.abund_col_names + [de.seq]][0])
                de.good_mothers = de.good_mothers.drop(index=mothers_ratio)
                de.denoised_ratio = pd.concat([de.denoised_ratio, de.good_mothers], ignore_index=True)
                de.denoised_ratio = de.denoised_ratio.sort_values([de.count], axis=0, ascending=False)
            else:
                de.denoised_ratio = pd.DataFrame(columns=[de.first_col_names + de.abund_col_names + [de.seq]][0])
                for mother in tqdm(mothers_ratio):
                    row = [
                        de.good_mothers[list(de.good_mothers.id == mother)][de.first_col_names].values.tolist()[
                            0] +
                        list(de.data_initial.loc[[[mother] +
                                                  list(de.merge_data.daughter[de.merge_data.mother_ratio == mother])][0],
                                                 de.abund_col_names].sum(0)) +
                        de.good_mothers[list(de.good_mothers.id == mother)][de.seq].values.tolist()]
                    row = pd.Series(row[0], index=[de.first_col_names + de.abund_col_names + [de.seq]][0])
                    row = row.to_frame().T
                    de.denoised_ratio = pd.concat([de.denoised_ratio, row], ignore_index=True)
                    de.good_mothers = de.good_mothers.drop(index=mother)
                de.denoised_ratio = pd.concat([de.denoised_ratio, de.good_mothers], ignore_index=True)
                de.denoised_ratio = de.denoised_ratio.sort_values([de.count], axis=0, ascending=False)
            if 'row' in locals():
                del row
        del de.good_mothers, mothers_ratio

    if (de.output_type == 'd') or (de.output_type == 'all'):
        mothers_d = de.merge_data.mother_d.unique()[1:]
        de.good_mothers = de.data_initial.loc[de.merge_data.daughter[de.merge_data.mother_d.isna()]
        ][de.first_col_names + de.abund_col_names + [de.seq]]
        print('writing output_d')
        # writing ratio
        if len(mothers_d) == 0:
            de.denoised_d = de.good_mothers
            de.denoised_d = de.denoised_d.sort_values([de.count], axis=0, ascending=False)
        else:
            if de.cores > 1:
                pool = mp.Pool(de.cores)
                [row] = zip(*pool.map(de.write_d_from_info, [mother for mother in mothers_d]))
                pool.close()
                del pool
                de.denoised_d = pd.DataFrame(row, columns=[de.first_col_names + de.abund_col_names + [de.seq]][0])
                de.good_mothers = de.good_mothers.drop(index=mothers_d)
                de.denoised_d = pd.concat([de.denoised_d, de.good_mothers], ignore_index=True)
                de.denoised_d = de.denoised_d.sort_values([de.count], axis=0, ascending=False)
            else:
                de.denoised_d = pd.DataFrame(columns=[de.first_col_names + de.abund_col_names + [de.seq]][0])
                for mother in tqdm(mothers_d):
                    row = [
                        de.good_mothers[list(de.good_mothers.id == mother)][de.first_col_names].values.tolist()[
                            0] +
                        list(de.data_initial.loc[[[mother] +
                                                  list(de.merge_data.daughter[de.merge_data.mother_d == mother])][0],
                                                 de.abund_col_names].sum(0)) +
                        de.good_mothers[list(de.good_mothers.id == mother)][de.seq].values.tolist()]
                    row = pd.Series(row[0], index=[de.first_col_names + de.abund_col_names + [de.seq]][0])
                    row = row.to_frame().T
                    de.denoised_d = pd.concat([de.denoised_d, row], ignore_index=True)
                    de.good_mothers = de.good_mothers.drop(index=mother)
                de.denoised_d = pd.concat([de.denoised_d, de.good_mothers], ignore_index=True)
                de.denoised_d = de.denoised_d.sort_values([de.count], axis=0, ascending=False)
            if 'row' in locals():
                del row
        del de.good_mothers, mothers_d
    if (de.output_type == 'ratio_d') or (de.output_type == 'all'):
        mothers_ratio_d = de.merge_data.mother_ratio_d.unique()[1:]
        de.good_mothers = de.data_initial.loc[de.merge_data.daughter[de.merge_data.mother_d.isna()]
        ][de.first_col_names + de.abund_col_names + [de.seq]]
        print('writing output_ratio_d')
        # writing ratio
        if len(mothers_ratio_d) == 0:
            de.denoised_ratio_d = de.good_mothers
            de.denoised_ratio_d = de.denoised_ratio_d.sort_values([de.count], axis=0, ascending=False)
        else:
            if de.cores > 1:
                pool = mp.Pool(de.cores)
                [row] = zip(*pool.map(de.write_ratio_d_from_info, [mother for mother in mothers_ratio_d]))
                pool.close()
                del pool
                de.denoised_ratio_d = pd.DataFrame(row, columns=[de.first_col_names + de.abund_col_names + [de.seq]][0])
                de.good_mothers = de.good_mothers.drop(index=mothers_ratio_d)
                de.denoised_ratio_d = pd.concat([de.denoised_ratio_d, de.good_mothers], ignore_index=True)
                de.denoised_ratio_d = de.denoised_ratio_d.sort_values([de.count], axis=0, ascending=False)
            else:
                de.denoised_ratio_d = pd.DataFrame(columns=[de.first_col_names + de.abund_col_names + [de.seq]][0])
                for mother in tqdm(mothers_ratio_d):
                    row = [
                        de.good_mothers[list(de.good_mothers.id == mother)][de.first_col_names].values.tolist()[
                            0] +
                        list(de.data_initial.loc[[[mother] +
                                                  list(de.merge_data.daughter[de.merge_data.mother_ratio_d == mother])][0],
                                                 de.abund_col_names].sum(0)) +
                        de.good_mothers[list(de.good_mothers.id == mother)][de.seq].values.tolist()]
                    row = pd.Series(row[0], index=[de.first_col_names + de.abund_col_names + [de.seq]][0])
                    row = row.to_frame().T
                    de.denoised_ratio_d = pd.concat([de.denoised_ratio_d, row], ignore_index=True)
                    de.good_mothers = de.good_mothers.drop(index=mother)
                de.denoised_ratio_d = pd.concat([de.denoised_ratio_d, de.good_mothers], ignore_index=True)
                de.denoised_ratio_d = de.denoised_ratio_d.sort_values([de.count], axis=0, ascending=False)
            if 'row' in locals():
                del row
        del de.good_mothers, mothers_ratio_d

    del de.merge_data
