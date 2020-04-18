#!/usr/bin/env python

""" This script outputs data related to the scores of the 18 Piano Sonatas by W.A.
Mozart as TSV files. It is hard-coded for being run at the top level of the repository
https://github.com/DCMLab/mozart_piano_sonatas.

In order to create the TSV files anew from the (MS3) MSCX files, use this
script that will be available in the near future at https://github.com/DCMLab/parsers :

    python extract_annotations.py scores -NHMqos
"""

import argparse, os, re, sys, logging
from fractions import Fraction as frac

try:
    import pandas as pd
except ImportError:
    sys.exit("""This script requires the pandas package. You can install it using the command
python -m pip install pandas""")

from expand_labels import expand_labels
from harmony import regex

__author__ = "Johannes Hentschel"
__copyright__ = """

    Copyright 2020, École Polytechnique Fédéral de Lausanne, Digital and Cognitive Musicology Lab

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
__credits__ = ["Johanes Hentschel", "Andrew McLeod"]
__license__ = "GPL-3.0-or-later"
__version__ = "1.0.0"
__maintainer__ = "Johannes Hentschel"
__email__ = "johannes.hentschel@epfl.ch"
__status__ = "Production"





################################################################################
# Configuration
################################################################################
os.environ['NUMEXPR_MAX_THREADS'] = '64' # to silence NumExpr prompt





################################################################################
# Converters
################################################################################
str2inttuple = lambda l: tuple() if l == '' else tuple(int(s) for s in l.split(', '))
str2strtuple = lambda l: tuple() if l == '' else tuple(str(s) for s in l.split(', '))
iterable2str = lambda iterable: ', '.join(str(s) for s in iterable)





################################################################################
# Constants
################################################################################
REGEX = re.compile(regex, re.VERBOSE)

IDX = pd.IndexSlice                      # for easy MultiIndex slicing

CONVERTERS = {
    'added_tones': str2inttuple,
    'act_dur': frac,
    'chord_tones': str2inttuple,
    'globalkey_is_minor': bool,
    'localkey_is_minor': bool,
    'next': str2inttuple,
    'nominal_duration': frac,
    'offset': frac,
    'onset': frac,
    'duration': frac,
    'scalar': frac,}

DTYPES = {
    'alt_label': str,
    'barline': str,
    'bass_note': 'Int64',
    'cadence': str,
    'cadences_id': 'Int64',
    'changes': str,
    'chord': str,
    'chord_type': str,
    'dont_count': 'Int64',
    'figbass': str,
    'form': str,
    'globalkey': str,
    'gracenote': str,
    'harmonies_id': 'Int64',
    'keysig': int,
    'label': str,
    'localkey': str,
    'mc': int,
    'midi': int,
    'mn': int,
    'notes_id': 'Int64',
    'numbering_offset': 'Int64',
    'numeral': str,
    'pedal': str,
    'phraseend': str,
    'relativeroot': str,
    'repeats': str,
    'root': 'Int64',
    'special': str,
    'staff': int,
    'tied': 'Int64',
    'timesig': str,
    'tpc': int,
    'voice': int,
    'voices': int,
    'volta': 'Int64'
}

FILE_LIST = pd.DataFrame({'filename':
  {(1, 1): 'K279-1',
  (1, 2): 'K279-2',
  (1, 3): 'K279-3',
  (2, 1): 'K280-1',
  (2, 2): 'K280-2',
  (2, 3): 'K280-3',
  (3, 1): 'K281-1',
  (3, 2): 'K281-2',
  (3, 3): 'K281-3',
  (4, 1): 'K282-1',
  (4, 2): 'K282-2',
  (4, 3): 'K282-3',
  (5, 1): 'K283-1',
  (5, 2): 'K283-2',
  (5, 3): 'K283-3',
  (6, 1): 'K284-1',
  (6, 2): 'K284-2',
  (6, 3): 'K284-3',
  (7, 1): 'K309-1',
  (7, 2): 'K309-2',
  (7, 3): 'K309-3',
  (8, 1): 'K311-1',
  (8, 2): 'K311-2',
  (8, 3): 'K311-3',
  (9, 1): 'K310-1',
  (9, 2): 'K310-2',
  (9, 3): 'K310-3',
  (10, 1): 'K330-1',
  (10, 2): 'K330-2',
  (10, 3): 'K330-3',
  (11, 1): 'K331-1',
  (11, 2): 'K331-2',
  (11, 3): 'K331-3',
  (12, 1): 'K332-1',
  (12, 2): 'K332-2',
  (12, 3): 'K332-3',
  (13, 1): 'K333-1',
  (13, 2): 'K333-2',
  (13, 3): 'K333-3',
  (14, 1): 'K457-1',
  (14, 2): 'K457-2',
  (14, 3): 'K457-3',
  (15, 1): 'K533-1',
  (15, 2): 'K533-2',
  (15, 3): 'K533-3',
  (16, 1): 'K545-1',
  (16, 2): 'K545-2',
  (16, 3): 'K545-3',
  (17, 1): 'K570-1',
  (17, 2): 'K570-2',
  (17, 3): 'K570-3',
  (18, 1): 'K576-1',
  (18, 2): 'K576-2',
  (18, 3): 'K576-3'}})

FILE_LIST.index.names = ['sonata', 'movement']





################################################################################
# Functions
################################################################################
def check_dir(d):
    if not os.path.isdir(d):
        d = os.path.join(os.getcwd(),d)
        if not os.path.isdir(d):
            if input(d + ' does not exist. Create? (y|n)') == "y":
                os.mkdir(d)
            else:
                raise argparse.ArgumentTypeError(d + ' needs to be an existing directory')
    if not os.path.isabs(d):
        d = os.path.abspath(d)
    return d



def ensure_types(df, col2dtype_dict, index_levels=True):
    names = None
    if index_levels and any(n in col2dtype_dict for n in df.index.names):
        names = [n for n in ['filename', 'notes_id', 'harmonies_id', 'cadences_id'] if n in df.index.names]
        df = df.reset_index()
    logging.debug(f"Changed the Dtypes as follows: {col2dtype_dict}")
    df = df.astype(col2dtype_dict)
    return df if names is None else df.set_index(names)



def format_data(name=None, dir=None, unfold=False, sonatas=None, movements=None, test=False, notes=False, harmonies=False, cadences=False, measures=False, join=False, expand=False, full_expand=False, relative_to_global=False, absolute=False, propagate=False):
    """"""
    fname = ' '.join(sys.argv[1:]) if name is None else name

    if dir is None:
        dir = os.path.join(os.getcwd(), 'formatted')

    selection = select_files(sonatas=sonatas, movements=movements)

    if test:
        print(selection)
    elif not any([harmonies, cadences, notes, measures, expand, full_expand, relative_to_global, absolute]):
        logging.error("Select the kind of data: -N for notes, -H for harmony labels, -M for measures, and -C for cadence labels. Pass -j to join several kinds into a single TSV.")
    elif len(selection) == 0:
        logging.error("No data matching your selection.")
    else:
        script_path = os.path.abspath('')
        kinds = []
        for kind in ['notes', 'harmonies', 'cadences']:
            if locals()[kind]:
                kinds.append(kind)
        if absolute:
            full_expand = True
        if full_expand or relative_to_global:
            expand = True
        if expand and not harmonies:
            logging.info("Parameters implie -H: Getting harmonies as well...")
            kinds.append('harmonies')
        if join:
            assert len(kinds) > 1, "Select at least two kinds of data for joining."
        if measures or join or unfold:
            kinds.append('measures')
        logging.info(f"Reading {len(selection) * len(kinds)} TSV files...")
        joining = {kind: read_tsvs(os.path.join(script_path, kind), selection) for kind in kinds}


        if unfold:
            logging.info("Calculating unfolding structures...")
            mn_seq_needed = not join and 'cadences' in kinds
            mc_sequences, mn_sequences = {}, {}
            for file, measure_list in joining['measures'].groupby(level=0):
                ml = measure_list.set_index('mc')
                seq = next2sequence(ml.next)
                mc_sequences[file] = seq
                if mn_seq_needed:
                    mn_seq = ml.mn.loc[seq]
                    mn_sequences[file] = mn_seq[mn_seq != mn_seq.shift()].to_list()


        if expand:
            global REGEX
            logging.info("Expanding chord labels...")
            expanded = expand_labels(joining['harmonies'], column='label', regex=REGEX, chord_tones=full_expand, relative_to_global=relative_to_global, absolute=absolute)
            col2type = {'globalkey_is_minor': int, 'localkey_is_minor': int} if 'localkey_is_minor' in expanded.columns else {'globalkey_is_minor': int}
            expanded = expanded.astype(col2type)
            if full_expand: # turn tuples into strings
                tone_tuples = ['chord_tones', 'added_tones']
                expanded.loc[:, tone_tuples] = expanded.loc[:, tone_tuples].applymap(iterable2str)
            if not propagate:
                joining['harmonies'] = expanded


        def store_result(df, fname, what):
            tsv_name = f"{fname}_{what}.tsv"
            tsv_path = os.path.join(dir, tsv_name)
            if what != 'measures':

                if unfold:
                    logging.info(f"Unfolding {what}...")
                    df = unfold_multiple(df, mc_sequences=mc_sequences, mn_sequences=mn_sequences)
                elif 'volta' in df.columns:
                    logging.info(f"Removing first voltas from {what}...")
                    df = df.drop(index=df[df.volta.fillna(0) == 1].index, columns='volta')

                if what == 'joined' and propagate:

                    if 'label' in df.columns:
                        logging.info(f"Propagating {'expanded' if expand else ''} chord labels...")
                        df = df.reset_index(level='harmonies_id')
                        df.harmonies_id = df.groupby(level=0, group_keys=False).apply(lambda df: df.harmonies_id.fillna(method='ffill'))
                        df.drop(columns='label', inplace=True)
                        if expand:
                            nonlocal expanded
                        else:
                            expanded = joining['harmonies']
                        df = pd.merge(df.set_index('harmonies_id', append=True), expanded, left_index=True, right_index=True, how='left', suffixes=('', '_y'))
                        duplicates = [col for col in df.columns if col.endswith('_y')]
                        df = df.drop(columns=duplicates)

                    if 'cadence' in df.columns:
                        logging.info("Propagating cadence labels...")
                        df = df.reset_index(level='cadences_id').set_index(pd.Series(range(len(df)), name='tmp_index'), append=True)
                        filled = df.groupby(level=0, group_keys=False).apply(lambda df: df[['cadences_id', 'cadence']].fillna(method='bfill'))
                        df[['cadences_id', 'cadence']] = filled
                        df = df.droplevel('tmp_index').set_index('cadences_id', append=True)

                    dtypes =  {k: v for k, v in {'bass_note': 'Int64',
                                                'cadences_id': 'Int64',
                                                'globalkey_is_minor': 'Int64',
                                                'harmonies_id': 'Int64',
                                                'localkey_is_minor': 'Int64',
                                                'notes_id': 'Int64',
                                                'root': 'Int64',}.items() if k in df.columns or k in df.index.names}
                    df = ensure_types(df, dtypes)

            df.to_csv(tsv_path, sep='\t')
            logging.info(f"PREVIEW of {tsv_path}:\n{df.head(5)}\n")

            if 'chord_tones' in df.columns:
                if absolute:
                    logging.info("The chord tones designate absolute pitches ordered on the line of fifth where -1 = F, 0 = C, 1 = G and so on.")
                elif relative_to_global:
                    logging.info("The chord tones designate scale degrees ordered on the line of fifth where 0 is the GLOBAL tonic, 1 the tone a perfect fifth above, and so on.")
                else:
                    logging.info("The chord tones designate scale degrees ordered on the line of fifth where 0 is the LOCAL tonic, 1 the tone a perfect fifth above, and so on.")


        if join:
            joined = join_tsv(**joining)
            store_result(joined, fname, 'joined')
        else:
            if propagate:
                logging.info("If DataFrames are not being joined, no data needs to be propagated.")
            for kind, tsv in joining.items():
                if kind != 'measures':
                    store_result(tsv, fname, kind)

        if measures:
            tsv = joining['measures']
            tsv.next = tsv.next.map(iterable2str)
            store_result(tsv, fname, 'measures')



def join_tsv(notes=None, harmonies=None, cadences=None, measures=None):
    """"""
    if notes is not None:
        if harmonies is not None:
            logging.info("Joining notes with harmony labels...")
            left = pd.merge(notes.set_index(['mc', 'mn', 'onset'], append=True), harmonies.set_index(['mc', 'mn', 'onset'], append=True), left_index=True, right_index=True, how='outer', sort=True, suffixes=('', '_y'))
            duplicates = [col for col in left.columns if col.endswith('_y')]
            left = left.reset_index(level='mc').drop(columns=duplicates)
        else:
            left = notes.set_index(['mn', 'onset'], append=True)
    else:
        left = harmonies.set_index(['mn', 'onset'], append=True)

    if cadences is not None:
        logging.info("Adjoining cadence labels...")
        res = pd.merge(left, cadences.set_index(['mn', 'onset'], append=True), left_index=True, right_index=True, how='outer')
    else:
        res = left

    if res.mc.isna().any():
        res.loc[res.mc.isna(), 'mc'] = pd.merge(res[res.mc.isna()].reset_index(level='onset')['onset'], measures[['mc', 'mn']], on=['filename', 'mn']).set_index(['mn', 'onset'], append=True)

    return res.reset_index(['mn', 'onset'])



def load_tsv(path, index_col=[0, 1], converters={}, dtypes={}, stringtype=False, **kwargs):
    """ Loads the TSV file `path` while applying correct type conversion and parsing tuples.

    Parameters
    ----------
    path : :obj:`str`
        Path to a TSV file as output by format_data().
    index_col : :obj:`list`, optional
        By default, the first two columns are loaded as MultiIndex.
        The first level distinguishes pieces and the second level the elements within.
    converters, dtypes : :obj:`dict`, optional
        Enhances or overwrites the mapping from column names to types included the constants.
    stringtype : :obj:`bool`, optional
        If you're using pandas >= 1.0.0 you might want to set this to True in order
        to be using the new `string` datatype that includes the new null type `pd.NA`.
    """
    conv = dict(CONVERTERS)
    types = dict(DTYPES)
    types.update(dtypes)
    conv.update(converters)
    if stringtype:
        types = {col: 'string' if typ == str else typ for col, typ in types.items()}
    return pd.read_csv(path, sep='\t', index_col=index_col,
                                dtype=types,
                                converters=conv, **kwargs)



def next2sequence(nxt):
    """Turns a pd.Series of lists into a sequence of elements."""
    i = nxt.index[0]
    last_i = nxt.index[-1]
    acc = [i]
    nxt = nxt.to_dict()
    flag = 0
    nxt_list = nxt[i]
    l = len(nxt_list)
    while i <= last_i:
        if i == last_i:
            if flag or l == 0:
                break
            elif l == 1: # last mc has repeat sign
                i = nxt_list[0]
                flag = 1
            else:
                raise NotImplementedError
        elif l == 1:
            i = nxt_list[0]
        elif l == 2:
            i = nxt_list[flag]
            flag = int(not flag)
        else:
            raise NotImplementedError("More than two voltas.")
        acc.append(i)
        nxt_list = nxt[i]
        l = len(nxt_list)
    return acc



def read_tsvs(dir, selection):
    """ Concatenates the selected files in `dir`.

    Parameters
    ----------
    dir : :obj:`str`
        Folder with TSV files.
    selection : :obj:`pandas.Series`
        Filenames without file extension. Files are assumed to exist.
    """
    files = (selection.filename + '.tsv').values
    df = pd.concat([pd.read_csv(os.path.join(dir, f), sep='\t', dtype=DTYPES, converters=CONVERTERS) for f in files],
                     keys=selection.filename, names=['filename', f"{os.path.basename(dir)}_id"])
    return df



def select_files(sonatas=None, movements=None):
    """

    """
    if sonatas is None:
        df = FILE_LIST
    else:
        df = FILE_LIST.loc[sonatas]
    if movements is not None:
        df = df.loc[IDX[:, movements],]
    return df



def unfold_multiple(unfold_this, mc_sequences, mn_sequences=None):
    """ `unfold_this` is a DataFrame with a MultiIndex of which the first level
        disambiguates thes pieces to be unfolded.
    """
    def unfold(df, sequence):
        """
        """
        return df.loc[[mc for mc in sequence if mc in df.index]]

    if 'mc' in unfold_this.columns:
        col = 'mc'
        sequences = mc_sequences
    else:
        col = 'mn'
        sequences = mn_sequences
    names = unfold_this.index.names
    groupby = names[0] if names[0] is not None else 'level_0'
    res = unfold_this.reset_index().set_index(col)
    try:
        res = res.groupby(groupby, group_keys=False).apply(lambda df: unfold(df, sequences[df[groupby].iloc[0]]))
    except:
        print(res[groupby])
    res = res.reset_index().set_index(names)
    if 'volta' in res.columns:
        res.drop(columns='volta', inplace=True)
    return res



################################################################################
# Command Line Interface
################################################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description = '''\
------------------------------------
| Format Mozart data to your needs |
------------------------------------

This script needs to remain at the top level of (your local copy of) the repo  mozart_piano_sonatas.
Run with parameter -t to see all file names.
''')
    parser.add_argument('name', metavar='NAME', nargs='?', type=check_dir, help='You may choose a name for the new TSV file(s). Existing files will be overwritten.')
    parser.add_argument('dir', metavar='DIR', nargs='?', type=check_dir, default=os.path.join(os.getcwd(), 'formatted'), help='Folder for storing the new TSV file(s). Can be relative, defaults to ./formatted')
    parser.add_argument('-u','--unfold', action='store_true', help="Unfold: Repeat everything that is repeated in the score, taking into account first and second endings ('voltas'). Otherwise, only second endings are returned.")
    parser.add_argument('-s','--sonatas', nargs='+', type=int, help="Select sonatas out of 1-18, e.g. -s 2 5 12")
    parser.add_argument('-m','--movements', nargs='+', type=int, help="Select only movements 1, 2 or 3, e.g. -m 1 3")
    parser.add_argument('-t','--test', action='store_true', help="Only test/view file selection without storing any data. Use -t without -sm to view all files.")
    parser.add_argument('-N','--notes', action='store_true', help="Get note lists.")
    parser.add_argument('-H','--harmonies', action='store_true', help="Get harmony labels.")
    parser.add_argument('-C','--cadences', action='store_true', help="Get cadence labels.")
    parser.add_argument('-M','--measures', action='store_true', help="Get measure properties.")
    parser.add_argument('-j','--join', action='store_true', help="Join the data into one single TSV.")
    parser.add_argument('-e','--expand', action='store_true', help="Split the chord labels into their encoded features.")
    parser.add_argument('-E','--full_expand', action='store_true', help="Compute chord tones, added tones, bass note and root note for every chord, expressed as line-of-fifth scale degrees.")
    parser.add_argument('-g','--globalkey', action='store_true', help="""Express all labels (and chord tones if -E is set) relative to the global tonic, not to the local key.
This parameter gets rid of the columns 'localkey' and relativeroot.""")
    parser.add_argument('-a','--absolute', action='store_true', help="Implies -E, but returns the chord tones as actual pitches rather than scale degrees.")
    parser.add_argument('-p','--propagate', action='store_true', help="When joining, spread out chord and cadence labels.")
    parser.add_argument('-l','--logging',default='INFO',help="Set logging to one of the levels {DEBUG, INFO, WARNING, ERROR, CRITICAL}. You may abbreviate by {D, I, W, E, C}.")
    args = parser.parse_args()
    logging_levels = {
        'DEBUG':    logging.DEBUG,
        'INFO':     logging.INFO,
        'WARNING':  logging.WARNING,
        'ERROR':    logging.ERROR,
        'CRITICAL':  logging.CRITICAL,
        'D':    logging.DEBUG,
        'I':     logging.INFO,
        'W':  logging.WARNING,
        'E':    logging.ERROR,
        'C':  logging.CRITICAL,
        }
    logging.basicConfig(level=logging_levels[args.logging], format='%(levelname)-8s %(message)s')

    format_data(args.name,
                args.dir,
                args.unfold,
                args.sonatas,
                args.movements,
                args.test,
                args.notes,
                args.harmonies,
                args.cadences,
                args.measures,
                args.join,
                args.expand,
                args.full_expand,
                args.globalkey,
                args.absolute,
                args.propagate)
