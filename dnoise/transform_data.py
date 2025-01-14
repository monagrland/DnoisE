#!/usr/bin/env python3

"""
.. codeauthor:: Adrià Antich <adriantich@gmail.com>

This program is called by DnoisE.

transform_data.py transforms data imported by import_data.py script to a pandas.DataFrame. Data is filtered and sorted
by read abundance. Other variables necessary for following steps of DnoisE are also defined.
This script also computes the entropy if specified.

"""


def sort_MOTU(de):
    de.data_initial = de.data_initial.sort_values([de.motu_column], axis=0, ascending=False)


def transform_data(de):
    print('transforming data')

    de.data_initial[de.seq] = de.data_initial[de.seq].str.upper()

    # obtain a column with total reads per seq.
    if not de.justcount:
        de.abund_col_names = list(de.data_initial.columns)[(de.start - 1):de.end]
        if de.start == 2:
            de.first_col_names = [list(de.data_initial.columns)[0]]
        else:
            de.first_col_names = list(de.data_initial.columns)[0:(de.start - 2)]
        if de.count in de.first_col_names:
            de.first_col_names.remove(de.count)
        if de.seq in de.first_col_names:
            de.first_col_names.remove(de.seq)
        de.data_initial.loc[:, de.count] = de.data_initial.loc[:, de.abund_col_names].sum(axis=1)
    else:
        de.first_col_names = [de.id]

    # sort by total reads
    de.data_initial = de.data_initial.sort_values([de.count], axis=0, ascending=False)

    # delete seqs with 0 reads
    de.data_initial = de.data_initial.loc[(de.data_initial.loc[:, de.count] != 0)]

    # maximum ratio allowed
    de.max_ratio = (1 / 2) ** (de.alpha * 1 * min(de.Ad1, de.Ad2, de.Ad3) + 1)
    # reorder index
    de.data_initial.index = list(range(de.data_initial.shape[0]))


