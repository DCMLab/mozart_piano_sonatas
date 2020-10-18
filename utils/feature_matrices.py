import sys, os, re, logging
from inspect import getfullargspec
from fractions import Fraction as frac

import pandas as pd

################################################################################
# Converters
################################################################################
str2inttuple = lambda l: tuple() if l == '' else tuple(int(s) for s in l.split(', '))
str2strtuple = lambda l: tuple() if l == '' else tuple(str(s) for s in l.split(', '))
def iterable2str(iterable):
    try:
        return ', '.join(str(s) for s in iterable)
    except:
        return iterable

def int2bool(s):
    try:
        return bool(int(s))
    except:
        return s






################################################################################
# Constants
################################################################################
CONVERTERS = {
    'added_tones': str2inttuple,
    'act_dur': frac,
    'chord_tones': str2inttuple,
    'globalkey_is_minor': int2bool,
    'localkey_is_minor': int2bool,
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
    'keysig': 'Int64',
    'label': str,
    'localkey': str,
    'mc': 'Int64',
    'midi': 'Int64',
    'mn': 'Int64',
    'notes_id': 'Int64',
    'numbering_offset': 'Int64',
    'numeral': str,
    'pedal': str,
    'playthrough': 'Int64',
    'phraseend': str,
    'relativeroot': str,
    'repeats': str,
    'root': 'Int64',
    'special': str,
    'staff': 'Int64',
    'tied': 'Int64',
    'timesig': str,
    'tpc': 'Int64',
    'voice': 'Int64',
    'voices': 'Int64',
    'volta': 'Int64'
}






BEATSIZE_MEMO = {}
################################################################################
# Functions
################################################################################
def beat_size(x):
    """ Pass a time signature and you get the beat size which is based on the fraction's
        denominator ('2/2' => 1/2, '4/4' => 1/4, '4/8' => 1/8). If the nominator is
        a higher multiple of 3, the threefold beat size is returned
        ('12/8' => 3/8, '6/4' => 3/4).

    Returns
    -------
    :obj:`Fraction`
    """
    try:
        d, n = str(x).split('/')
    except:
        return x
    d = int(d)
    return frac(f"{3 if d % 3 == 0 and d > 3 else 1}/{n}")



def beat_size_memo(x):
    """ Memoized version of beat_size() using the global dict BEATSIZE_MEMO.
    """
    if pd.isnull(x):
        return x
    global BEATSIZE_MEMO
    if x in BEATSIZE_MEMO:
        return BEATSIZE_MEMO[x]
    bs = beat_size(x)
    logging.debug(f"Using beat size {bs} for {x} time signatures.")
    BEATSIZE_MEMO[x] = bs
    return bs



def compute_beat(onset, timesig):
    """ Turn an offset in whole notes into a beat based on the time signature.
        Uses: beat_size_memo()

    Parameters
    ----------
    onset : :obj:`Fraction`
        Offset from the measure's beginning as fraction of a whole note.
    timesig : :obj:`str`
        Time signature, i.e., a string representing a fraction.
    """
    if pd.isnull(onset):
        return onset
    if pd.isnull(timesig):
        return timesig
    size = beat_size_memo(timesig)
    beat = onset // size + 1
    subbeat = frac((onset % size) / size)
    if subbeat > 0:
        return f"{beat}.{subbeat}"
    else:
        return str(beat)



def compute_mn(df):
    """ Compute measure numbers from a measure list with columns ['dont_count', 'numbering_offset']
    """
    excluded = df['dont_count'].fillna(0).astype(bool)
    offset   = df['numbering_offset']
    mn = (~excluded).cumsum()
    if offset.notna().any():
        offset = offset.fillna(0).astype(int).cumsum()
        mn += offset
    return mn.rename('mn')



def ensure_types(df, col2dtype_dict, index_levels=True):
    """ Converts columns and index levels of `df` into the given dtypes, just to be sure.

    Parameters
    ----------
    df : :obj:`pandas.DataFrame`
        DataFrame will not be mutated.
    col2dtype_dict : :obj:`dict`
        Dictionary mapping names of columns and/or index levels to dtypes.
    index_levels : :obj:`bool`, optional
        Pass False if index levels should not be converted.
    """
    names = None
    if index_levels and any(n in col2dtype_dict for n in df.index.names):
        names = [n for n in ['filename', 'notes_id', 'harmonies_id', 'cadences_id'] if n in df.index.names]
        df = df.reset_index(names)
    logging.debug(f"Changed the Dtypes as follows: {col2dtype_dict}")
    df = df.astype(col2dtype_dict)
    return df if names is None else df.set_index(names)



def join_tsv(notes=None, harmonies=None, cadences=None, measures=None, join_measures=False):
    """"""
    first = True
    if notes is not None:
        notes = notes.set_index(['mc', 'onset'], append=True)
        if harmonies is not None:
            logging.info("Joining notes with harmony labels...")
            first = False
            left = pd.merge(notes, harmonies.set_index(['mc', 'onset'], append=True), left_index=True, right_index=True, how='outer', sort=True, suffixes=('', '_y'))
            duplicates = [col for col in left.columns if col.endswith('_y')]
            left = left.drop(columns=duplicates)
        else:
            left = notes
    elif harmonies is not None:
        left = harmonies.set_index(['mc', 'onset'], append=True)
    else:
        left = None

    if left is not None:
        if cadences is not None:
            if first:
                logging.info("Joining notes with cadence labels...")
                first = False
            else:
                logging.info("Adjoining cadence labels...")
            res = pd.merge(left, cadences.set_index(['mc', 'onset'], append=True), left_index=True, right_index=True, how='outer', suffixes=('', '_y'))
        else:
            res = left
    else:
        res = cadences

    # try:
    #     if res.mc.isna().any():
    #         res.loc[res.mc.isna(), 'mc'] = pd.merge(res[res.mc.isna()].reset_index(level='onset')['onset'],
    #                                                 measures[['mc', 'mn']], on=['filename', 'mn'])\
    #                                          .set_index(['mn', 'onset'], append=True)
    # except:
    #     print(res)
    #     raise

    if join_measures:
        logging.info(f"{'J' if first else 'Adj'}oining measure info...")
        res = res.merge(measures.set_index('mc', append=True).droplevel('measures_id'), how='left', left_on=['filename', 'mc'], right_index=True, suffixes=('', '_y'))
    duplicates = [col for col in res.columns if col.endswith('_y')]
    res = res.drop(columns=duplicates)
    names = list(res.index.names)
    fixed_order = ['filename', 'notes_id', 'harmonies_id', 'cadences_id']
    names_order = [n for n in fixed_order if n in names]
    names_order.extend([n for n in names if n not in fixed_order])
    if names != names_order:
        logging.debug("Reordering index levels...")
        res = res.reorder_levels(names_order)
    return res



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



def name2tpc(nn):
    """ Turn a note name such as `Ab` into a tonal pitch class, such that -1=F, 0=C, 1=G etc.
        Uses: split_note_name()
    """
    if nn.__class__ == int or pd.isnull(nn):
        return nn
    name_tpcs = {'C': 0, 'D': 2, 'E': 4, 'F': -1, 'G': 1, 'A': 3, 'B': 5}
    accidentals, note_name = split_note_name(nn, count=True)
    step_tpc = name_tpcs[note_name.upper()]
    return step_tpc + 7 * accidentals



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



def merge_ties(df, return_dropped=False, reset_index=True):
    """ In a note list, merge tied notes to single events with accumulated durations.
        Input dataframe needs columns ['duration', 'tied', 'midi', 'staff']. This
        function does not handle correctly overlapping ties on the same pitch since
        it doesn't take into account the notational layers ('voice').
    """
    def merge(df):
        vc = df.tied.value_counts()
        if vc[1] != 1 or vc[-1] != 1:
            logging.warning(f"")
        ix=df.iloc[0].name
        dur = df.duration.sum()
        drop = df.iloc[1:].index.to_list()
        return pd.Series({'ix':ix, 'duration': dur, 'dropped': drop})

    def merge_ties(staff_midi):

        staff_midi['chunks'] = (staff_midi.tied  == 1).astype(int).cumsum()
        t = staff_midi.groupby('chunks', group_keys=False).apply(merge)
        return t.set_index('ix')

    if reset_index:
        try:
            names = df.index.names
            df = df.reset_index()
        except:
            logging.warning("Error while resetting index. Trying as is...")
            names = None
            df = df.copy()
    else:
        df = df.copy()
    notna = df.loc[df.tied.notna(), ['duration', 'tied', 'midi', 'staff']]
    new_dur = notna.groupby(['staff', 'midi'], group_keys=False).apply(merge_ties).sort_index()
    df.loc[new_dur.index, 'duration'] = new_dur.duration
    if return_dropped:
        df.loc[new_dur.index, 'dropped'] = new_dur.dropped
    df = df.drop(new_dur.dropped.sum())
    if reset_index and names != None:
        return df.set_index(names)
    return df



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



def split_note_name(nn, count=False):
    """ Splits a note name such as 'Ab' into accidentals and name.

    nn : :obj:`str`
        Note name.
    count : :obj:`bool`, optional
        Pass True to get the accidentals as integer rather than as string.
    """
    m = re.match("^([A-G]|[a-g])(#*|b*)$", str(nn))
    if m is None:
        logging.error(nn + " is not a valid scale degree.")
        return None, None
    note_name, accidentals = m.group(1), m.group(2)
    if count:
        accidentals = accidentals.count('#') - accidentals.count('b')
    return accidentals, note_name



def transform(df, func, param2col=None, column_wise=False, **kwargs):
    """ Compute a function for every row of a DataFrame, using several cols as arguments.
        The result is the same as using df.apply(lambda r: func(param1=r.col1, param2=r.col2...), axis=1)
        but it optimizes the procedure by precomputing `func` for all occurrent parameter combinations.
        Uses: inspect.getfullargspec()

    Parameters
    ----------
    df : :obj:`pandas.DataFrame` or :obj:`pandas.Series`
        Dataframe containing function parameters.
    func : :obj:`callable`
        The result of this function for every row will be returned.
    param2col : :obj:`dict` or :obj:`list`, optional
        Mapping from parameter names of `func` to column names.
        If you pass a list of column names, the columns' values are passed as positional arguments.
        Pass None if you want to use all columns as positional arguments.
    column_wise : :obj:`bool`, optional
        Pass True if you want to map `func` to the elements of every column separately.
        This is simply an optimized version of df.apply(func) but allows for naming
        columns to use as function arguments. If param2col is None, `func` is mapped
        to the elements of all columns, otherwise to all columns that are not named
        as parameters in `param2col`.
        In the case where `func` does not require a positional first element and
        you want to pass the elements of the various columns as keyword argument,
        give it as param2col={'function_argument': None}
    inplace : :obj:`bool`, optional
        Pass True if you want to mutate `df` rather than getting an altered copy.
    **kwargs : Other parameters passed to `func`.
    """
    if column_wise:
        if not df.__class__ == pd.core.series.Series:
            if param2col is None:
                return df.apply(transform, args=(func,), **kwargs)
            if param2col.__class__ == dict:
                var_arg = [k for k, v in param2col.items() if v is None]
                apply_cols = [col for col in df.columns if not col in param2col.values()]
                assert len(var_arg) < 2, f"Name only one variable keyword argument as which {apply_cols} are used {'argument': None}."
                var_arg = var_arg[0] if len(var_arg) > 0 else getfullargspec(func).args[0]
                param2col = {k: v for k, v in param2col.items() if v is not None}
                result_cols = {col: transform(df, func, {**{var_arg: col}, **param2col}, **kwargs) for col in apply_cols}
                param2col = param2col.values()
            else:
                apply_cols = [col for col in df.columns if not col in param2col]
                result_cols = {col: transform(df, func, [col] + param2col, **kwargs) for col in apply_cols}
            return pd.DataFrame(result_cols, index=df.index)

    if param2col.__class__ == dict:
        param_tuples = list(df[param2col.values()].itertuples(index=False, name=None))
        result_dict = {t: func(**{a:b for a, b in zip(param2col.keys(), t)}, **kwargs) for t in set(param_tuples)}
    else:
        if df.__class__ == pd.core.series.Series:
            if param2col is not None:
                logging.warning("When 'df' is a Series, the parameter 'param2col' has no use.")
            param_tuples = df.values
            result_dict = {t: func(t, **kwargs) for t in set(param_tuples)}
        else:
            if param2col is None:
                param_tuples = list(df.itertuples(index=False, name=None))
            else:
                param_tuples = list(df[list(param2col)].itertuples(index=False, name=None))
            result_dict = {t: func(*t, **kwargs) for t in set(param_tuples)}
    return pd.Series([result_dict[t] for t in param_tuples], index=df.index)



def transpose_to_C(note_list):
    """ Transposes the columns ['tpc', 'midi'] of a note list to C/c depending on
        the column 'globalkey'. Input is mutated."""
    transpose_by = transform(note_list.globalkey, name2tpc)
    note_list.tpc -= transpose_by

    midi_transposition = transform(transpose_by, lambda x: 7 * x % 12)
    # For transpositions up to a diminished fifth, move pitches up,
    # for larger intervals, move pitches down.
    midi_transposition.where(midi_transposition <= 6, midi_transposition % -12, inplace=True)
    note_list.midi -= midi_transposition

    note_list.globalkey = note_list.globalkey.str.islower().replace({True: 'c', False: 'C'})



def unfold_multiple(unfold_this, mc_sequences, mn_sequences=None):
    """ `unfold_this` is a DataFrame with a MultiIndex of which the first level
        disambiguates thes pieces to be unfolded.
    """

    def unfold(df, sequence):
        """
        """
        nonlocal unfolded
        vc = df.index.value_counts()
        seq = sequence[sequence.isin(df.index)]
        playthrough_vals = sum([[playthrough]*vc[mc] for playthrough, mc in seq.items()], [])
        playthrough_col.extend(playthrough_vals)
        return df.loc[seq.values]

    if 'mc' in unfold_this.columns:
        col = 'mc'
        sequences = mc_sequences
    else:
        col = 'mn'
        sequences = mn_sequences

    names = unfold_this.index.names
    groupby = names[0] if names[0] is not None else 'level_0'
    res = unfold_this.reset_index().set_index(col)
    playthrough_col = []
    unfolded = []
    for group, df in res.groupby(groupby, group_keys=False):
        unfolded.append(unfold(df, sequences[group]))
    res = pd.concat(unfolded)
    res = res.reset_index().set_index(names)
    res.insert(res.columns.get_loc('mn')+1, 'playthrough', playthrough_col)
    return res
