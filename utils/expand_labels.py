################################################################################
# Internal libraries
################################################################################
import argparse, os, re, sys, logging
from collections.abc import Iterable
from inspect import getfullargspec
from fractions import Fraction as frac
logging.getLogger().setLevel(logging.INFO)


################################################################################
# External libraries
################################################################################
import pandas as pd
import numpy as np


################################################################################
# Helpers
################################################################################
from .feature_matrices import name2tpc, transform

################################################################################
# Constants
################################################################################


class SliceMaker(object):
    """ This class serves for storing slice notation such as :3 as a variable or
        passing it as function argument.

    Examples
    --------
        SM = SliceMaker()
        some_function( slice_this, SM[3:8] )

        select_all = SM[:]
        df.loc[select_all]
    """
    def __getitem__(self, item):
        return item
SM = SliceMaker()


################################################################################
# Functions for treating DCML harmony labels
################################################################################

def abs2rel_key(absolute, localkey, global_minor=False):
    """ Expresses a Roman numeral as scale degree relative to a given localkey.
    The result changes depending on whether Roman numeral and localkey are
    interpreted within a global major or minor key.
    Uses: split_sd()
    ``

    Parameters
    ----------
    absolute : :obj:`str`
        Relative key expressed as Roman scale degree of the local key.
    localkey : :obj:`str`
        The local key in terms of which `absolute` will be expressed.
    global_minor : bool, optional
        Has to be set to True if `absolute` and `localkey` are scale degrees of a global minor key.

    Examples
    --------
    In a minor context, the key of II would appear within the key of vii as #III.

        >>> abs2rel_key('iv', 'VI', global_minor=False)
        'bvi'       # F minor expressed with respect to A major
        >>> abs2rel_key('iv', 'vi', global_minor=False)
        'vi'        # F minor expressed with respect to A minor
        >>> abs2rel_key('iv', 'VI', global_minor=True)
        'vi'        # F minor expressed with respect to Ab major
        >>> abs2rel_key('iv', 'vi', global_minor=True)
        '#vi'       # F minor expressed with respect to Ab minor

        >>> abs2rel_key('VI', 'IV', global_minor=False)
        'III'       # A major expressed with respect to F major
        >>> abs2rel_key('VI', 'iv', global_minor=False)
        '#III'       # A major expressed with respect to F minor
        >>> abs2rel_key('VI', 'IV', global_minor=True)
        'bIII'       # Ab major expressed with respect to F major
        >>> abs2rel_key('VI', 'iv', global_minor=False)
        'III'       # Ab major expressed with respect to F minor
    """
    if pd.isnull(absolute):
        return np.nan
    maj_rn = ['I','II','III','IV','V','VI','VII']
    min_rn = ['i','ii','iii','iv','v','vi','vii']
    shifts = np.array(  [[0,0,0,0,0,0,0],
                        [0,0,1,0,0,0,1],
                        [0,1,1,0,0,1,1],
                        [0,0,0,-1,0,0,0],
                        [0,0,0,0,0,0,1],
                        [0,0,1,0,0,1,1],
                        [0,1,1,0,1,1,1]])
    abs_acc, absolute = split_sd(absolute, count=True)
    localkey_acc, localkey = split_sd(localkey, count=True)
    shift = abs_acc - localkey_acc
    steps = maj_rn if absolute.isupper() else min_rn
    key_num = maj_rn.index(localkey.upper())
    abs_num = (steps.index(absolute) - key_num) % 7
    step = steps[abs_num]
    if localkey.islower() and abs_num in [2,5,6]:
        shift += 1
    if global_minor:
        key_num = (key_num - 2) % 7
    shift -= shifts[key_num][abs_num]
    acc = shift * '#' if shift > 0 else -shift * 'b'
    return acc+step



def changes2list(changes, sort=True):
    """Splits a string of changes into a list of 4-tuples.

    Example
    -------
    >>> changes2list('+#7b5')
    [('+#7', '+', '#', '7'),
     ('b5',  '',  'b', '5')]
    """
    res = [t for t in re.findall("((\+)?(#+|b+)?(1\d|\d))",changes)]
    return sorted(res, key=lambda x: int(x[3]), reverse=True) if sort else res



def changes2tpc(changes, numeral, minor=False, root_alterations=False):
    """ Given a numeral and changes, computes the intervals that the changes represent.
        Changes do not express absolute intervals but instead depend on the numeral and the mode.
        Uses: split_sd(), changes2list()

    Parameters
    ----------
    changes : :obj:`str`
        A string of changes following the DCML harmony standard.
    numeral : :obj:`str`
        Roman numeral. If it is preceded by accidentals, it depends on the parameter
        `root_alterations` whether these are taken into account.
    minor : :obj:`bool`, optional
        Set to true if the `numeral` occurs in a minor context.
    root_alterations : :obj:`bool`, optional
        Set to True if accidentals of the root should change the result.
    """
    root_alteration, num_degree = split_sd(numeral, count=True)
    # build 2-octave diatonic scale on C major/minor
    root = ['I','II','III','IV','V','VI','VII'].index(num_degree.upper())
    tpcs = 2 * [i for i in (0,2,-3,-1,1,-4,-2)] if minor else 2 * [i for i in (0,2,4,-1,1,3,5)]
    tpcs = tpcs[root:] + tpcs[:root]               # starting the scale from chord root
    root = tpcs[0]
    if root_alterations:
        root += 7 * root_alteration
        tpcs[0] = root

    alts = changes2list(changes, sort=False)
    acc2tpc = lambda accidentals: 7 * (accidentals.count('#') - accidentals.count('b'))
    return [(full, added, acc, chord_interval, (tpcs[int(chord_interval) - 1] + acc2tpc(acc) - root) if not chord_interval in ['3', '5'] else None) for full, added, acc, chord_interval in alts]



def chord2tpcs(chord, regex, **kwargs):
    """ Split a chord label into its features and apply features2tpcs().
        Uses: features2tpcs()

    Parameters
    ----------
    chord : :obj:`str`
        Chord label that can be split into the features ['numeral', 'form', 'figbass', 'changes', 'relativeroot'].
    regex : :obj:`re.Pattern`
        Compiled regex with named groups for the five features.
    **kwargs : arguments for features2tpcs
    """
    chord_features = re.match(regex, chord)
    assert chord_features is not None, f"{chord} does not match the regex."
    chord_features = chord_features.groupdict()
    numeral, form, figbass, changes, relativeroot = tuple(chord_features[f] for f in ('numeral', 'form', 'figbass', 'changes', 'relativeroot'))
    return features2tpcs(numeral=numeral, form=form, figbass=figbass, changes=changes, relativeroot=relativeroot, **kwargs)



def compute_chord_tones(df, bass_only=False, expand=False, cols={}):
    """ Compute the chord tones for DCML harmony labels. They are returned as lists
        of tonal pitch classes in close position, starting with the bass note. The
        tonal pitch classes represent intervals relative to the local tonic:
        -2: Second below tonic
        -1: fifth below tonic
         0: tonic
         1: fifth above tonic
         2: second above tonic, etc.
        The labels need to have undergone split_labels() and propagate_keys().
        Pedal points are not taken into account.
        Uses: features2tpcs(), transform()

    Parameters
    ----------
    df : :obj:`pandas.DataFrame`
        Dataframe containing DCML chord labels that have been split by split_labels()
        and where the keys have been propagated using propagate_keys(add_bool=True).
    bass_only : :obj:`bool`, optional
        Pass True if you need only the bass note.
    expand : :obj:`bool`, optional
        Pass True if you need chord tones and added tones in separate columns.
    cols : :obj:`dict`, optional
        In case the column names for ['numeral', 'form', 'figbass', 'changes', 'relativeroot', 'localkey', 'globalkey'] deviate, pass a dict, such as
        {'numeral':         'numeral_col_name',
         'form':            'form_col_name',
         'figbass':         'figbass_col_name',
         'changes':         'changes_col_name',
         'relativeroot':    'relativeroot_col_name',
         'localkey':        'localkey_col_name',
         'globalkey':       'globalkey_col_name'}
        You may also deactivate columns by setting them to None, e.g. {'changes': None}

    Returns
    -------
    :obj:`pandas.Series` or :obj:`pandas.DataFrame`
        For every row of `df` one tuple with chord tones, expressed as tonal picth classes.
        If `expand` is True, the function returns a DataFrame with four columns:
        Two with tuples for chord tones and added tones, one with the chord root,
        and one with the bass note.
    """

    df = df.copy()
    tmp_index = not df.index.is_unique
    if tmp_index:
        logging.debug("Index is not unique. Temporarily added a unique index level.")
        df.set_index(pd.Series(range(len(df))), append=True, inplace=True)

    features = ['numeral', 'form', 'figbass', 'changes', 'relativeroot', 'localkey', 'globalkey']
    for col in features:
        if col in df.columns and not col in cols:
            cols[col] = col
    local_minor, global_minor = f"{cols['localkey']}_is_minor", f"{cols['globalkey']}_is_minor"
    if not local_minor in df.columns:
        df[local_minor] = series_is_minor(df[cols['localkey']], is_name=False)
        logging.debug(f"Boolean column '{local_minor} created.'")
    if not global_minor in df.columns:
        df[global_minor] = series_is_minor(df[cols['globalkey']], is_name=True)
        logging.debug(f"Boolean column '{global_minor} created.'")

    param_cols = {col: cols[col] for col in ['numeral', 'form', 'figbass', 'changes', 'relativeroot'] if cols[col] is not None}
    param_cols['minor'] = local_minor
    param_tuples = list(df[param_cols.values()].itertuples(index=False, name=None))
    result_dict = {t: features2tpcs(**{a:b for a, b in zip(param_cols.keys(), t)}, bass_only=bass_only, merge_tones=not expand) for t in set(param_tuples)}
    if expand:
        res = pd.DataFrame([result_dict[t] for t in param_tuples], index=df.index)
        res['bass_note'] = res.chord_tones.apply(lambda l: l if pd.isnull(l) else l[0])
    else:
        res = pd.Series([result_dict[t] for t in param_tuples], index=df.index)
    return res.droplevel(-1) if tmp_index else res



def expand_labels(df, column, regex, groupby={'level': 0, 'group_keys': False}, cols={}, dropna=False, propagate=True, relative_to_global=False, chord_tones=False, absolute=False, all_in_c=False):
    """ Split harmony labels complying with the DCML syntax into columns holding their various features
        and allows for additional computations and transformations.
        Uses: split_labels(), replace_special(), propagate_keys(), propagate_pedal(),
              compute_chord_tones(), transform(), transpose(), labels2global_tonic(),
              features2type()

    Parameters
    ----------
    df : :obj:`pandas.DataFrame`
        Dataframe where one column contains DCML chord labels.
    column : :obj:`str`
        Name of the column that holds the harmony labels.
    regex : :obj:`re.Pattern`
        Compiled regular expression used to split the labels. It needs to have named groups.
        The group names are used as column names unless replaced by `cols`.
    groupby : :obj:`dict`, optional
        By default, `df` is treated as having several pieces that can be individually treated
        by grouping the first index level: `df.groupby(level=0)`. The dictionary holds the parameters
        that are being passed to df.groupby()`. {'group_keys': False} means that the piece identifies
        will not be added as additional index level. If the pieces are identified by a column `col`,
        pass {'by': 'col'}.  If `df` has chords of only one piece, pass None.
    cols : :obj:`dict`, optional
        Dictionary to map the regex's group names to deviating column names of your choice.
    dropna : :obj:`bool`, optional
        Pass True if you want to drop rows where `column` is NaN/<NA>
    propagate: :obj:`bool`, optional
        By default, information about global and local keys and about pedal points is spread throughout
        the DataFrame. Pass False if you only want to split the labels into their features. This ignores
        all following parameters because their expansions depend on information about keys.
    relative_to_global : :obj:`bool`, optional
        Pass True if you want all labels expressed with respect to the global key.
        This levels and eliminates the features `localkey` and `relativeroot`.
    chord_tones : :obj:`bool`, optional
        Pass True if you want to add four columns that contain information about each label's
        chord, added, root, and bass tones. The pitches are expressed as intervals
        relative to the respective chord's local key or, if `relative_to_global=True`,
        to the globalkey. The intervals are represented as integers that represent
        stacks of fifths over the tonic, such that 0 = tonic, 1 = dominant, -1 = subdominant,
        2 = supertonic etc.
    absolute : :obj:`bool`, optional
        Pass True if you want to transpose the relative `chord_tones` to the global
        key, which makes them absolute so they can be expressed as actual note names.
        This implies prior conversion of the chord_tones (but not of the labels) to
        the global tonic.
    all_in_c : :obj:`bool`, optional
        Pass True to transpose `chord_tones` to C major/minor. This performs the same
        transposition of chord tones as `relative_to_global` but without transposing
        the labels, too. This option clashes with `absolute=True`.
    """
    assert sum((absolute, all_in_c)) < 2, "Chord tones can be either 'absolute' or 'all_in_c', not both."
    df = df.copy()
    tmp_index = not df.index.is_unique
    if tmp_index:
        logging.debug("Index is not unique. Temporarily added a unique index level.")
        df.set_index(pd.Series(range(len(df))), append=True, inplace=True)
    ix = df.index
    df = df.sort_index()

    for col in ['numeral', 'form', 'figbass', 'localkey', 'globalkey']:
        if not col in cols:
            cols[col] = col
    global_minor = f"{cols['globalkey']}_is_minor"

    not_nan = df[column].dropna()
    immediate_repetitions = not_nan == not_nan.shift()
    k = immediate_repetitions.sum()
    if k > 0:
        if k / len(not_nan.index) > 0.1:
            raise ValueError("DataFrame has many direct repetitions of labels. This function is written for lists of labels only which should have no immediate repetitions.")
        else:
            logging.debug(f"Immediate repetition of labels:\n{not_nan[immediate_repetitions]}")

    df = split_labels(df, column, regex, cols=cols, dropna=dropna)
    df = replace_special(df, regex=regex, merge=True, cols=cols)
    df['chord_type'] = transform(df, features2type, [cols[col] for col in ['numeral', 'form', 'figbass']])

    if propagate:
        key_cols = {col: cols[col] for col in ['localkey', 'globalkey']}
        if groupby is not None:
            try:
                df = df.groupby(**groupby).apply(propagate_keys, add_bool=True, **key_cols)
            except:
                logging.error("Are you expanding labels of a single piece? In that case, call expand_labels() with 'groupby=None'")
                raise
        else:
            try:
                df = propagate_keys(df, add_bool=True, **key_cols)
            except:
                logging.error("Are you expanding labels of several pieces in the same DataFrame? In that case, define 'groupby()' parameters.")
                raise

        df = propagate_pedal(df, cols=cols)

        if chord_tones:
            ct = compute_chord_tones(df, expand=True, cols=cols)
            if relative_to_global or absolute or all_in_c:
                transpose_by = transform(df, rn2tpc, [cols['localkey'], global_minor])
                if absolute:
                    transpose_by += transform(df, name2tpc, [cols['globalkey']])
                ct = pd.DataFrame([transpose(tpcs, fifths) for tpcs, fifths in zip(ct.itertuples(index=False, name=None), transpose_by.values)], index=ct.index, columns=ct.columns)
            df = pd.concat([df, ct], axis=1)

    if relative_to_global:
        labels2global_tonic(df, inplace=True, cols=cols)

    return df.reindex(ix).droplevel(-1) if tmp_index else df.reindex(ix)



def features2tpcs(numeral, form=None, figbass=None, changes=None, relativeroot=None, key='C', minor=None, merge_tones=True, bass_only=False):
    """ Given the features of a chord label, this function returns the chord tones
        in the order of the inversion, starting from the bass note. The tones are
        expressed as tonal pitch classes, where -1=F, 0=C, 1=G etc.
        Uses: str_is_minor(), name2tpc(), rn2tpc(), changes2list(), sort_tpcs()

    Parameters
    ----------
    numeral: :obj:`str`
        Roman numeral of the chord's root
    form: {None, 'M', 'o', '+' '%'}, optional
        Indicates the chord type if not a major or minor triad (for which `form`is None).
        '%' and 'M' can only occur as tetrads, not as triads.
    figbass: {None, '6', '64', '7', '65', '43', '2'}, optional
        Indicates chord's inversion. Pass None for triad root position.
    changes: :obj:`str`, optional
        Added steps such as '+6' or suspensions such as '4' or any combination such as (9+64).
        Numbers need to be in descending order.
    relativeroot: :obj:`str`, optional
        Pass a Roman scale degree if `numeral` is to be applied to a different scale
        degree of the local key, as in 'V65/V'
    key : :obj:`str` or :obj:`int`, optional
        The local key expressed as the root's note name or a tonal pitch class.
        If it is a name and `minor` is `None`, uppercase means major and lowercase minor.
        If it is a tonal pitch class, `minor` needs to be specified.
    minor : :obj:`bool`, optional
        Pass True for minor and False for major. Can be omitted if `key` is a note name.
        This affects calculation of chords related to III, VI and VII.
    merge_tones : :obj:`bool`, optional
        Pass False if you want the function to return two tuples, one with (potentially suspended)
        chord tones and one with added notes.
    bass_only : :obj:`bool`, optional
        Return only the bass note instead of all chord tones.

    """
    if pd.isnull(numeral):
        if bass_only:
            return np.nan
        elif merge_tones:
                return np.nan
        else:
            return {
                'chord_tones': np.nan,
                'added_tones': np.nan,
                'root': np.nan,
            }
    form, figbass, changes, relativeroot = tuple('' if pd.isnull(val) else val for val in (form, figbass, changes, relativeroot))
    label = f"{numeral}{form}{figbass}{'(' + changes + ')' if changes != '' else ''}{'/' + relativeroot if relativeroot != '' else ''}"

    if minor is None:
        try:
            minor = str_is_minor(key, is_name=True)
            logging.debug(f"Mode inferred from {key}.")
        except:
            raise ValueError(f"If parameter 'minor' is not specified, 'key' needs to be a string, not {key}")

    key = name2tpc(key)

    if form in ['%', 'M']:
        assert figbass in ['7', '65', '43', '2'], f"{label}: {form} requires figbass since it specifies a chord's seventh."

    if relativeroot != '':
        resolved = resolve_relative_keys(relativeroot, minor)
        rel_minor = str_is_minor(resolved, is_name=False)
        transp = rn2tpc(resolved, minor)
        logging.debug(f"Chord applied to {relativeroot}. Therefore transposing it by {transp} fifths.")
        return features2tpcs(numeral=numeral, form=form, figbass=figbass, relativeroot=None, changes=changes, key=key + transp, minor=rel_minor, merge_tones=merge_tones, bass_only=bass_only)

    if numeral.lower() == '#vii' and not minor:
        logging.warning(f"{label} in major context is most probably an annotation error.")

    root_alteration, num_degree = split_sd(numeral, count=True)

    # build 2-octave diatonic scale on C major/minor
    root = ['I','II','III','IV','V','VI','VII'].index(num_degree.upper())
    tpcs = 2 * [i+key for i in (0,2,-3,-1,1,-4,-2)] if minor else 2 * [i+key for i in (0,2,4,-1,1,3,5)]
    tpcs = tpcs[root:] + tpcs[:root]               # starting the scale from chord root
    root = tpcs[0] + 7 * root_alteration
    tpcs[0] = root                                 # octave stays diatonic, is not altered
    logging.debug(f"The {'minor' if minor else 'major'} scale starting from the root: {tpcs}")

    def set_iv(chord_interval, interval_size):
        """ Fix the interval of a given chord interval (both viewed from the bass note).
        """
        nonlocal tpcs, root
        iv = root + interval_size
        i = chord_interval - 1
        tpcs[i] = iv
        tpcs[i+7] = iv

    if form == 'o':
        set_iv(3, -3)
        set_iv(5, -6)
        if figbass in ['7', '65', '43', '2']:
            set_iv(7, -9)
    elif form == '%':
        set_iv(3, -1)
        set_iv(5, 6)
        set_iv(7, -2)
    elif form == '+':
        set_iv(3, 4)
        set_iv(5, 8)
    else: # triad with or without major or minor seven
        set_iv(5, 1)
        if num_degree.isupper():
            set_iv(3, 4)
        else:
            set_iv(3, -3)
        if form == 'M':
            set_iv(7, 5)
        elif figbass in ['7', '65', '43', '2']:
            set_iv(7, -2)

    # apply changes
    alts = changes2list(changes, sort=False)
    added_notes = []

    for full, added, acc, chord_interval in alts:
        added = added == '+'
        chord_interval = int(chord_interval) - 1
        if chord_interval == 0 or chord_interval > 14:
            logging.warning(f"Alteration of scale degree {chord_interval+1} is meaningless and ignored.")
            continue
        next_octave = chord_interval > 7
        shift = 7 * (acc.count('#') - acc.count('b'))
        new_val = tpcs[chord_interval] + shift
        if added:
            added_notes.append(new_val)
        elif chord_interval in [1, 3, 5, 8, 10, 12]:    # these are changes to scale degree 2, 4, 6 that replace the lower neighbour unless they have a #
            if '#' in acc:
                tpcs[chord_interval + 1] = new_val
                if chord_interval == 5 and not figbass in ['7', '65', '43', '2']: # leading tone to 7 but not in seventh chord
                    added_notes.append(new_val)
            else:
                tpcs[chord_interval - 1] = new_val
        else:                                           # chord tone alterations
            if chord_interval == 6 and figbass != '7':  # 7th are a special case:
                if figbass == '':                       # in root position triads they are added
                    added_notes.append(new_val)
                elif figbass in ['6', '64']:            # in inverted triads they replace the root
                    tpcs[0] = new_val
                elif '#' in acc:                        # in a seventh chord, they might retardate the 8
                    tpcs[7] = new_val
                    added_notes.append(new_val)
                else:                                   # otherwise they are unclear
                    logging.warning(f"In seventh chords, such as {label}, it is not clear whether the {full} alters the 7 or replaces the 8 and should not be used.")
            elif tpcs[chord_interval] == new_val and not next_octave:
                logging.warning(f"The change {full} has no effect in {numeral}{form}{figbass}")
            else:
                tpcs[chord_interval] = new_val
        if next_octave and not added:
            added_notes.append(new_val)

    if figbass in ['', '6', '64']:
        chord_tones = [tpcs[i] for i in [0,2,4]]
    elif figbass in ['7', '65', '43', '2']:
        chord_tones = [tpcs[i] for i in [0,2,4,6]]
    else:
        raise ValueError(f"{figbass} is not a valid chord inversion.")

    figbass2bass = {
        '': 0,
        '7': 0,
        '6': 1,
        '65': 1,
        '64': 2,
        '43': 2,
        '2': 3
    }
    bass = figbass2bass[figbass]
    bass_tpc = chord_tones[bass]

    if bass_only:
        return bass_tpc
    elif merge_tones:
            return tuple(sort_tpcs(chord_tones + added_notes, start=bass_tpc))
    else:
        return {
            'chord_tones': tuple(chord_tones[bass:] + chord_tones[:bass]),
            'added_tones': tuple(added_notes),
            'root': root,
        }



def features2type(numeral, form=None, figbass=None):
    """ Turns a combination of the three chord features into a chord type.

    Returns
    -------
    'M':    Major triad
    'm':    Minor triad
    'o':    Diminished triad
    '+':    Augmented triad
    'mm7':  Minor seventh chord
    'Mm7':  Dominant seventh chord
    'MM7':  Major seventh chord
    'mM7':  Minor major seventh chord
    'o7':   Diminished seventh chord
    '%7':   Half-diminished seventh chord
    '+7':   Augmented (minor) seventh chord
    '+M7':  Augmented major seventh chord
    """
    if pd.isnull(numeral):
        return numeral
    form, figbass = tuple('' if pd.isnull(val) else val for val in (form, figbass))
    #triads
    if figbass in ['', '6', '64']:
        if form in ['o', '+']:
            return form
        if form in ['%', 'M', '+M']:
            if figbass != '':
                logging.error(f"{form} is a seventh chord and cannot have figbass '{figbass}'")
                return None
            # else: go down, interpret as seventh chord
        else:
            return 'm' if numeral.islower() else 'M'
    # seventh chords
    if form in ['o', '%', '+', '+M']:
        return f"{form}7"
    triad = 'm' if numeral.islower() else 'M'
    seventh = 'M' if form == 'M' else 'm'
    return f"{triad}{seventh}7"



def fifths2iv(fifths):
    """ Return interval name of a stack of fifths such that
       0 = 'P1', -1 = 'P4', -2 = 'm7', 4 = 'M3' etc.
    """
    if pd.isnull(fifths):
        return fifths
    if isinstance(fifths, Iterable):
        return map2elements(fifths, fifths2iv)
    interval_qualities = {0: ['P', 'P', 'P', 'M', 'M', 'M', 'M'],
                   -1:['D', 'D', 'D', 'm', 'm', 'm', 'm']}
    fifths += 1       # making 0 = fourth, 1 = unison, 2 = fifth etc.
    pos = fifths % 7
    int_num = [4, 1, 5, 2, 6, 3, 7][pos]
    qual_region = fifths // 7
    if qual_region in interval_qualities:
        int_qual = interval_qualities[qual_region][pos]
    elif qual_region < 0:
        int_qual = (abs(qual_region) - 1) * 'D'
    else:
        int_qual = qual_region * 'A'
    return int_qual + str(int_num)



def fifths2acc(fifths):
    """ Returns accidentals for a stack of fifths that can be combined with a
        basic representation of the seven steps."""
    return abs(fifths // 7) * 'b' if fifths < 0 else fifths // 7 * '#'



def fifths2name(fifths):
    """ Return note name of a stack of fifths such that
       0 = C, -1 = F, -2 = Bb, 1 = G etc.
    """
    if pd.isnull(fifths):
        return fifths
    if isinstance(fifths, Iterable):
        return map2elements(fifths, fifths2name)
    note_names = ['F', 'C', 'G', 'D', 'A', 'E', 'B']
    return fifths2str(fifths, note_names)



def fifths2pc(fifths):
    """Turn a stack of fifths into a chromatic pitch class"""
    if pd.isnull(fifths):
        return fifths
    if isinstance(fifths, Iterable):
        return map2elements(fifths, fifths2pc)
    return 7 * fifths % 12


def is_minor_mode(fifths, minor=False):
    """ Returns True if the TPC `fifths` naturally has a minor third in the scale.
    """
    thirds = [-4, -3, -2, -1, 0, 1, 2] if minor else [3, 4, 5, -1, 0, 1, 2]
    third = thirds[(fifths + 1) % 7] - fifths
    return third == -3


def fifths2rn(fifths, minor=False, auto_key=False):
    """Return Roman numeral of a stack of fifths such that
       0 = I, -1 = IV, 1 = V, -2 = bVII in major, VII in minor, etc.

    Parameters
    ----------
    auto_key : :obj:`bool`, optional
        By default, the returned Roman numerals are uppercase. Pass True to pass upper-
        or lowercase according to the position in the scale.
    """
    if pd.isnull(fifths):
        return fifths
    if isinstance(fifths, Iterable):
        return map2elements(fifths, fifths2rn, minor=minor)
    rn = ['VI', 'III', 'VII', 'IV', 'I', 'V', 'II'] if minor else ['IV', 'I', 'V', 'II', 'VI', 'III', 'VII']
    sel = fifths + 3 if minor else fifths
    res = fifths2str(sel, rn)
    if auto_key and is_minor_mode(fifths, minor):
        return res.lower()
    return res



def fifths2sd(fifths, minor=False):
    """Return scale degree of a stack of fifths such that
       0 = '1', -1 = '4', -2 = 'b7' in major, '7' in minor etc.
    """
    if pd.isnull(fifths):
        return fifths
    if isinstance(fifths, Iterable):
        return map2elements(fifths, fifths2sd, minor=minor)
    sd = ['6', '3', '7', '4', '1', '5', '2'] if minor else ['4', '1', '5', '2', '6', '3', '7']
    if minor:
        fifths += 3
    return fifths2str(fifths, sd)



def fifths2str(fifths, steps):
    """ Boiler plate used by fifths2-functions.
    """
    fifths += 1
    acc = fifths2acc(fifths)
    return acc + steps[fifths % 7]



def labels2global_tonic(df, cols={}, inplace=False):
    """ Transposes all numerals to their position in the global major or minor scale.
        This eliminates localkeys and relativeroots. The resulting chords are defined
        by [`numeral`, `figbass`, `changes`, `globalkey_is_minor`] (and `pedal`).
        Uses: transform(), rel2abs_key(), transpose_changes(), series_is_minor(), resolve_relative_keys() -> str_is_minor()

    Parameters
    ----------
    df : :obj:`pandas.DataFrame`
        Dataframe containing DCML chord labels that have been split by split_labels()
        and where the keys have been propagated using propagate_keys(add_bool=True).
    cols : :obj:`dict`, optional
        In case the column names for ['numeral', 'form', 'figbass', 'changes', 'relativeroot', 'localkey', 'globalkey'] deviate, pass a dict, such as
        {'chord':           'chord_col_name'
         'pedal':           'pedal_col_name',
         'numeral':         'numeral_col_name',
         'form':            'form_col_name',
         'figbass':         'figbass_col_name',
         'changes':         'changes_col_name',
         'relativeroot':    'relativeroot_col_name',
         'localkey':        'localkey_col_name',
         'globalkey':       'globalkey_col_name'}}
    inplace : :obj:`bool`, optional
        Pass True if you want to mutate the input.

    Returns
    -------
    :obj:`pandas.DataFrame`
        If `inplace=False`, the relevant features of the transposed chords are returned.
        Otherwise, the original DataFrame is mutated.
    """
    if not inplace:
        df = df.copy()
    tmp_index = not df.index.is_unique
    if tmp_index:
        logging.debug("Index is not unique. Temporarily added a unique index level.")
        df.set_index(pd.Series(range(len(df))), append=True, inplace=True)

    features = ['chord', 'pedal', 'numeral', 'form', 'figbass', 'changes', 'relativeroot', 'localkey', 'globalkey']
    for col in features:
        if col in df.columns and not col in cols:
            cols[col] = col
    local_minor, global_minor = f"{cols['localkey']}_is_minor", f"{cols['globalkey']}_is_minor"
    if not local_minor in df.columns:
        df[local_minor] = series_is_minor(df[cols['localkey']], is_name=False)
        logging.debug(f"Boolean column '{local_minor} created.'")
    if not global_minor in df.columns:
        df[global_minor] = series_is_minor(df[cols['globalkey']], is_name=True)
        logging.debug(f"Boolean column '{global_minor} created.'")

    # Express pedals in relation to the global tonic
    param_cols = [cols[col] for col in ['pedal', 'localkey']] + [global_minor]
    df['pedal'] = transform(df, rel2abs_key, param_cols)

    # Make relativeroots to local keys
    param_cols = [cols[col] for col in ['relativeroot', 'localkey']] + [local_minor, global_minor]
    relativeroots = df.loc[df[cols['relativeroot']].notna(), param_cols]
    rr_tuples = list(relativeroots.itertuples(index=False, name=None))
    transposed_rr = {(rr, localkey, local_minor, global_minor): rel2abs_key(resolve_relative_keys(rr, local_minor), localkey, global_minor) for (rr, localkey, local_minor, global_minor) in set(rr_tuples)}
    df.loc[relativeroots.index, cols['localkey']] = pd.Series((transposed_rr[t] for t in rr_tuples), index=relativeroots.index)
    df.loc[relativeroots.index, local_minor] = series_is_minor(df.loc[relativeroots.index, cols['localkey']])

    # Express numerals in relation to the global tonic
    param_cols = [cols[col] for col in ['numeral', 'localkey']] + [global_minor]
    df['abs_numeral'] = transform(df, rel2abs_key, param_cols)

    # Transpose changes to be valid with the new numeral
    param_cols = [cols[col] for col in ['changes', 'numeral']] + ['abs_numeral', local_minor, global_minor]
    df[cols['changes']] = transform(df, transpose_changes, param_cols)

    # Combine the new chord features
    df[cols['chord']] = df.abs_numeral + df.form.fillna('') + df.figbass.fillna('') + ('(' + df.changes + ')').fillna('') # + ('/' + df.relativeroot).fillna('')

    if inplace:
        df[cols['numeral']] = df.abs_numeral
        drop_cols = [cols[col] for col in ['localkey', 'relativeroot']] + ['abs_numeral', local_minor]
        df.drop(columns=drop_cols, inplace=True)
    else:
        res_cols = ['abs_numeral'] + [cols[col] for col in ['form', 'figbass', 'changes', 'globalkey']] + [global_minor]
        res = df[res_cols].rename(columns={'abs_numeral': cols['numeral']})
        return res.droplevel(-1) if tmp_index else res



def map2elements(e, f, *args, **kwargs):
    """ If `e` is an iterable, `f` is applied to all elements.
    """
    if isinstance(e, Iterable):
        return e.__class__(map2elements(x, f, *args, **kwargs) for x in e)
    return f(e, *args, **kwargs)



def merge_changes(left, right, *args):
    """ Merge to `changes` into one, e.g. `b3` and `+#7` to `+#7b3`.
        Uses: changes2list()
    """
    all_changes = [changes2list(changes, sort=False) for changes in (left, right, *args)]
    res = sum(all_changes, [])
    res = sorted(res, key=lambda x: int(x[3]), reverse=True)
    return ''.join(e[0] for e in res)



def propagate_keys(df, globalkey='globalkey', localkey='localkey', add_bool=True):
    """ Propagate information about global keys and local keys throughout the dataframe.
        Pass split harmonies for one piece at a time. For concatenated pieces, use apply_to_pieces().
        Uses: series_is_minor()

    Parameters
    ----------
    df : :obj:`pandas.DataFrame`
        Dataframe containing DCML chord labels that have been split by split_labels().
    globalkey, localkey : :obj:`str`, optional
        In case you renamed the columns, pass column names.
    add_bool : :obj:`bool`, optional
        Pass True if you want to add two boolean columns which are true if the respective key is
        a minor key.
    """
    df = df.copy()
    nunique = df[globalkey].nunique()
    assert nunique > 0, "No global key specified. It might be that this function is being applied in a wrong groupby and gets rows instead of entire frames."
    if nunique > 1:
        raise NotImplementedError("Several global keys not accepted at the moment.")

    logging.debug('Extending global key to all harmonies')
    global_key = df[globalkey].iloc[0]
    if pd.isnull(global_key):
        global_key = df[globalkey].dropna().iloc[0]
        logging.warning(f"Global key is not specified in the first label. Using '{global_key}' from index {df[df[globalkey] == global_key].index[0]}")
    df.loc[:,globalkey] = global_key
    global_minor = series_is_minor(df[globalkey], is_name=True)

    logging.debug('Extending local keys to all harmonies')
    local_key = df[localkey].iloc[0]
    if pd.isnull(df[localkey].iloc[0]):
        one = 'i' if global_minor.iloc[0] else 'I'
        df.iloc[0, df.columns.get_loc(localkey)] = one
    df[localkey].fillna(method='ffill', inplace=True)

    if add_bool:
        local_minor = series_is_minor(df[localkey], is_name=False)
        gm = f"{globalkey}_is_minor"
        lm = f"{localkey}_is_minor"
        df[gm] = global_minor
        df[lm] = local_minor
    return df



def propagate_pedal(df, relative=True, drop_pedalend=True, cols={}):
    """ Propagate the pedal note for all chords within square brackets.
        By default, the note is expressed in relation to each label's localkey.
        Uses: rel2abs_key(), abs2rel_key

    Parameters
    ----------
    df : :obj:`pandas.DataFrame`
        Dataframe containing DCML chord labels that have been split by split_labels()
        and where the keys have been propagated using propagate_keys().
    relative : :obj:`bool`, optional
        Pass False if you want the pedal note to stay the same even if the localkey changes.
    drop_pedalend : :obj:`bool`, optional
        Pass False if you don't want the column with the ending brackets to be dropped.
    cols : :obj:`dict`, optional
        In case the column names for ['pedal','pedalend', 'globalkey', 'localkey'] deviate, pass a dict, such as
        {'pedal':       'pedal_col_name',
         'pedalend':    'pedalend_col_name',
         'globalkey':   'globalkey_col_name',
         'localkey':    'localkey_col_name'}
    """
    df = df.copy()
    tmp_index = not df.index.is_unique
    if tmp_index:
        logging.debug("Index is not unique. Temporarily added a unique index level.")
        df.set_index(pd.Series(range(len(df))), append=True, inplace=True)
        ix = df.index
        df = df.sort_index()
    features = ['pedal','pedalend', 'globalkey', 'localkey']
    for col in features:
        if not col in cols:
            cols[col] = col
    pedal, pedalend = cols['pedal'], cols['pedalend']

    logging.debug('Extending pedal notes to concerned harmonies')
    beginnings = df.loc[df[pedal].notna(), pedal]
    endings = df.loc[df[pedalend].notna(), pedalend]
    n_b, n_e = len(beginnings), len(endings)
    assert n_b == n_e, f"{n_b} organ points started, {n_e} ended! Beginnings:\n{beginnings}\nEndings:\n{endings}"
    if relative:
        assert df[cols['localkey']].notna().all(), "Local keys must first be propagated using propagate_keys(), no NaNs allowed."

    for (fro, ped), to in zip(beginnings.items(), endings.index):
        try:
            section = df.loc[fro:to].index
        except:
            logging.error(f"Slicing of the DataFrame did not work from {fro} to {to}. Index looks like this:\n{df.head().index}")
        localkeys = df.loc[section, cols['localkey']]
        if localkeys.nunique() > 1:
            first_localkey = localkeys.iloc[0]
            globalkeys = df.loc[section, cols['globalkey']].unique()
            assert len(globalkeys) == 1, "Several globalkeys appearing within the same organ point."
            global_minor = globalkeys[0].islower()
            key2pedal = {key: ped if key == first_localkey else abs2rel_key(rel2abs_key(ped, first_localkey, global_minor), key, global_minor) for key in localkeys.unique()}
            logging.debug(f"Pedal note {ped} has been transposed relative to other local keys within a global {'minor' if global_minor else 'major'} context: {key2pedal}")
            pedals = pd.Series([key2pedal[key] for key in localkeys], index=section)
        else:
            pedals = pd.Series(ped, index=section)
        df.loc[section, pedal] = pedals

    if drop_pedalend:
        df = df.drop(columns=pedalend)
    return df.reindex(ix).droplevel(-1) if tmp_index else df



def rel2abs_key(rel, localkey, global_minor=False):
    """Expresses a Roman numeral that is expressed relative to a localkey
    as scale degree of the global key. For local keys {III, iii, VI, vi, VII, vii}
    the result changes depending on whether the global key is major or minor.
    Uses: split_sd()

    Parameters
    ----------
    rel : :obj:`str`
        Relative key or chord expressed as Roman scale degree of the local key.
    localkey : :obj:`str`
        The local key to which `rel` is relative.
    global_minor : bool, optional
        Has to be set to True if `localkey` is a scale degree of a global minor key.

    Examples
    --------
    If the label viio6/VI appears in the context of the local key VI or vi,
    viio6 the absolute key to which viio6 applies depends on the global key.
    The comments express the examples in relation to global C major or C minor.

        >>> rel2abs_key('vi', 'VI', global_minor=False)
        '#iv'       # vi of A major = F# minor
        >>> rel2abs_key('vi', 'vi', global_minor=False)
        'iv'        # vi of A minor = F minor
        >>> rel2abs_key('vi', 'VI', global_minor=True)
        'iv'        # vi of Ab major = F minor
        >>> rel2abs_key('vi', 'vi', global_minor=True)
        'biv'       # vi of Ab minor = Fb minor

    The same examples hold if you're expressing in terms of the global key
    the root of a VI-chord within the local keys VI or vi.
    """
    if pd.isnull(rel):
        return np.nan
    maj_rn = ['I','II','III','IV','V','VI','VII']
    min_rn = ['i','ii','iii','iv','v','vi','vii']
    shifts = np.array(  [[0,0,0,0,0,0,0],
                        [0,0,1,0,0,0,1],
                        [0,1,1,0,0,1,1],
                        [0,0,0,-1,0,0,0],
                        [0,0,0,0,0,0,1],
                        [0,0,1,0,0,1,1],
                        [0,1,1,0,1,1,1]])
    rel_acc, rel = split_sd(rel, count=True)
    localkey_acc, localkey = split_sd(localkey, count=True)
    shift = rel_acc + localkey_acc
    steps = maj_rn if rel.isupper() else min_rn
    rel_num = steps.index(rel)
    key_num = maj_rn.index(localkey.upper())
    step = steps[(rel_num + key_num) % 7]
    if localkey.islower() and rel_num in [2,5,6]:
        shift -= 1
    if global_minor:
        key_num = (key_num - 2) % 7
    shift += shifts[rel_num][key_num]
    acc = shift * '#' if shift > 0 else -shift * 'b'
    return acc+step



def replace_special(df, regex, merge=False, inplace=False, cols={}, special_map={}):
    """ Move special symbols in the `numeral` column to a separate column and replace them by the explicit chords they stand for.
    In particular, this function replaces the symbols `It`, `Ger`, and `Fr`.
    Uses: merge_changes()

    Parameters
    ----------
    df : :obj:`pandas.DataFrame`
        Dataframe containing DCML chord labels that have been split by split_labels().
    regex : :obj:`re.Pattern`
        Compiled regular expression used to split the labels replacing the special symbols.It needs to have named groups.
        The group names are used as column names unless replaced by `cols`.
    merge : :obj:`bool`, optional
        False: By default, existing values, except `figbass`, are overwritten.
        True: Merge existing with new values (for `changes` and `relativeroot`).
    inplace : :obj:`bool`, optional
        True: Change `df` inplace (default).
        False: Return copy.
    cols : :obj:`dict`, optional
        The special symbols appear in the column `numeral` and are moved to the column `special`.
        In case the column names for ['numeral','form', 'figbass', 'changes', 'relativeroot', 'special'] deviate, pass a dict, such as
        {'numeral':         'numeral_col_name',
         'form':            'form_col_name
         'figbass':         'figbass_col_name',
         'changes':         'changes_col_name',
         'relativeroot':    'relativeroot_col_name',
         'special':         'special_col_name'}
    special_map : :obj:`dict`, optional
        In case you want to add or alter special symbols to be replaced, pass a replacement map, e.g.
        {'N': 'bII6'}. The column 'figbass' is only altered if it's None to allow for inversions of special chords.
    """
    if not inplace:
        df = df.copy()
    tmp_index = not df.index.is_unique
    if tmp_index:
        logging.debug("Index is not unique. Temporarily added a unique index level.")
        df.set_index(pd.Series(range(len(df))), append=True, inplace=True)

    spec = {
        'It': 'viio6(b3)/V',
        'Ger': 'viio65(b3)/V',
        'Fr':  'V7(b5)/V',
    }
    spec.update(special_map)

    features = ['numeral','form', 'figbass', 'changes', 'relativeroot']
    for col in features + ['special']:
        if not col in cols:
            cols[col] = col
    feature_cols = list(cols.values())
    missing = [cols[f] for f in features if not cols[f] in df.columns]
    assert len(missing) == 0, f"These columns are missing from the DataFrame: {missing}. Either use split_labels() first or give correct `cols` parameter."
    select_all_special = df[df[cols['numeral']].isin(spec.keys())].index

    logging.debug(f"Moving special symbols from {cols['numeral']} to {cols['special']}...")
    if not cols['special'] in df.columns:
        df.insert(df.columns.get_loc(cols['numeral'])+1, cols['special'], np.nan)
    df.loc[select_all_special, cols['special']] = df.loc[select_all_special, cols['numeral']]


    def repl_spec(frame, instead, special):
        """Check if the selected parts are empty and replace."""
        new_vals = re.match(regex, instead)
        if new_vals is None:
            logging.warning(f"{instead} is not a valid label. Skipped.")
            return frame
        else:
            new_vals = new_vals.groupdict()
        for f in features:
            if new_vals[f] is not None:
                replace_this = SM[:] # by default, replace entire column
                if f == 'figbass':   # only empty figbass is replaced, with the exception of `Ger6` and `Fr6`
                    if special in ['Fr', 'Ger']: # For these symbols, a wrong `figbass` == 6 is accepted and replaced
                        replace_this = (frame[cols['figbass']] == '6') | frame[cols['figbass']].isna()
                    else:
                        replace_this = frame[cols['figbass']].isna()
                elif f != 'numeral': # numerals always replaced completely
                    not_empty = frame[cols[f]].notna()
                    if not_empty.any():
                        if f in ['changes', 'relativeroot'] and merge:
                            if f == 'changes':
                                frame.loc[not_empty, cols[f]] = frame.loc[not_empty, cols[f]].apply(merge_changes, args=(new_vals[f],))
                            elif f == 'relativeroot':
                                frame.loc[not_empty, cols[f]] = frame.loc[not_empty, cols[f]].apply(lambda x: f"{new_vals[f]}/{x}")
                            logging.debug(f"While replacing {special}, the existing '{f}'-values have been merged with '{new_vals[f]}', resulting in :\n{frame.loc[not_empty, cols[f]]}")
                            replace_this = ~not_empty
                        else:
                            logging.warning(f"While replacing {special}, the following existing '{f}'-values have been overwritten with {new_vals[f]}:\n{frame.loc[not_empty, cols[f]]}")
                frame.loc[replace_this, cols[f]] = new_vals[f]
        return frame


    for special, instead in spec.items():
        select_special = df[cols['special']] == special
        df.loc[select_special, feature_cols] = repl_spec(df.loc[select_special, feature_cols].copy(), instead, special)

    if df[cols['special']].isna().all():
        df.drop(columns=cols['special'], inplace=True)

    return df.droplevel(-1) if tmp_index else df



def resolve_relative_keys(relativeroot, minor=False):
    """ Resolve nested relative keys, e.g. 'V/V/V' => 'VI'.
        Uses: rel2abs_key(), str_is_minor()

    relativeroot : :obj:`str`
        One or several relative keys, e.g. iv/v/VI (fourth scale degree of the fifth scale degree of the sixth scale degree)
    minor : :obj:`bool`, optional
        Pass True if the last of the relative keys is to be interpreted within a minor context.
    """
    spl = relativeroot.split('/')
    if len(spl) < 2:
        return relativeroot
    if len(spl) == 2:
        applied, to = spl
        return rel2abs_key(applied, to, minor)
    previous, last = '/'.join(spl[:-1]), spl[-1]
    return rel2abs_key(resolve_relative_keys(previous, str_is_minor(last, is_name=False)), last, minor)



def rn2tpc(rn, global_minor=False):
    """ Turn a Roman numeral into a TPC interval (e.g. for transposition purposes).
        Uses: split_sd()
    """
    rn_tpcs_maj = {'I': 0, 'II': 2, 'III': 4, 'IV': -1, 'V': 1, 'VI': 3, 'VII': 5}
    rn_tpcs_min = {'I': 0, 'II': 2, 'III': -3, 'IV': -1, 'V': 1, 'VI': -4, 'VII': -2}
    accidentals, rn_step = split_sd(rn, count=True)
    rn_step = rn_step.upper()
    step_tpc = rn_tpcs_min[rn_step] if global_minor else rn_tpcs_maj[rn_step]
    return step_tpc + 7 * accidentals



def series_is_minor(S, is_name=True):
    # regex = r'([A-Ga-g])[#|b]*' if is_name else '[#|b]*(\w+)'
    # return S.str.replace(regex, lambda m: m.group(1)).str.islower()
    return S.str.islower() # as soon as one character is not lowercase, it should be major



def sort_tpcs(tpcs, ascending=True, start=None):
    """ Sort tonal pitch classes by order on the piano.
        Uses: fifths2pc()

    Parameters
    ----------
    tpcs : collection of :obj:`int`
        Tonal pitch classes to sort.
    ascending : :obj:`bool`, optional
        Pass False to sort by descending order.
    start : :obj:`int`, optional
        Start on or above this TPC.
    """
    res = sorted(tpcs, key=lambda x: (fifths2pc(x),-x))
    if start is not None:
        pcs = [fifths2pc(tpc) for tpc in res]
        start = fifths2pc(start)
        i = 0
        while i < len(pcs) - 1 and pcs[i] < start:
            i += 1
        res = res[i:] + res[:i]
    return res if ascending else list(reversed(res))



def split_labels(df, column, regex, cols={}, dropna=False, **kwargs):
    """ Split harmony labels complying with the DCML syntax into columns holding their various features.

    Parameters
    ----------
    df : :obj:`pandas.DataFrame`
        Dataframe where one column contains DCML chord labels.
    column : :obj:`str`
        Name of the column that holds the harmony labels.
    regex : :obj:`re.Pattern`
        Compiled regular expression used to split the labels. It needs to have named groups.
        The group names are used as column names unless replaced by `cols`.
    cols : :obj:`dict`
        Dictionary to map the regex's group names to deviating column names.
    dropna : :obj:`bool`, optional
        Pass True if you want to drop rows where `column` is NaN/<NA>
    """

    assert regex.__class__ == re.compile('').__class__, "Compile regular expression using re.compile()"
    features = regex.groupindex.keys()
    df = df.copy()
    if df[column].isna().any():
        if dropna:
            logging.debug(f"Removing NaN values from label column {column}...")
            df = df[df[column].notna()]
        else:
            logging.warning(f"{column} contains NaN values.")
    if df[column].str.contains('-').any():
        logging.debug(f"Splitting alternative annotations...")
        alternatives = df[column].str.rsplit('-', expand=True)
        alt_name = f"alt_{column}"
        df.loc[:, column] = alternatives[0]
        df.insert(df.columns.get_loc(column)+1, alt_name, alternatives[1].fillna(np.nan)) # replace None by NaN
        if len(alternatives.columns) > 2:
            logging.warning(f"More than two alternatives are not taken into account: {alternatives[alternatives[2].notna()]}")
    logging.debug("Applying RegEx to labels...")
    spl = df[column].str.extract(regex, expand=True) #.astype('string') # needs pandas 1.0?
    for feature in features:
        name = cols[feature] if feature in cols else feature
        df[name] = spl[feature]
        logging.debug(f"Stored feature {feature} as column {name}.")
    numeral = cols['numeral'] if 'numeral' in cols else 'numeral'
    phrases = cols['phraseend'] if 'phraseend' in cols else 'phraseend'
    mistakes = df[column].notna() & df[numeral].isna() & df[phrases].isna()
    if mistakes.any():
        logging.warning(f"The following chords could not be parsed:\n{df.loc[mistakes, :column]}")
    return df



def split_sd(sd, count=False):
    """ Splits a scale degree such as 'bbVI' or 'b6' into accidentals and numeral.

    sd : :obj:`str`
        Scale degree.
    count : :obj:`bool`, optional
        Pass True to get the accidentals as integer rather than as string.
    """
    m = re.match("^(#*|b*)(VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i|\d)$", str(sd))
    if m is None:
        logging.error(sd + " is not a valid scale degree.")
        return None, None
    acc, num = m.group(1), m.group(2)
    if count:
        acc = acc.count('#') - acc.count('b')
    return acc, num



def str_is_minor(tone, is_name=True):
    """"""
    # regex = r'([A-Ga-g])[#|b]*' if is_name else '[#|b]*(\w+)'
    # m = re.match(regex, tone)
    # if m is None:
    #     return m
    # return m.group(1).islower()
    return tone.islower()



def transform_columns(df, func, columns=None, param2col=None, inplace=False, **kwargs):
    """ Wrapper function to use transform() on df[columns].

    Parameters
    ----------
    df : :obj:`pandas.DataFrame`
        DataFrame where columns (or column combinations) work as function arguments.
    func : :obj:`callable`
        Function you want to apply to all elements in `columns`.
    columns : :obj:`list`
        Columns to which you want to apply `func`.
    param2col : :obj:`dict` or :obj:`list`, optional
        Mapping from parameter names of `func` to column names.
        If you pass a list of column names, the columns' values are passed as positional arguments.
        Pass None if you want to use all columns as positional arguments.
    inplace : :obj:`bool`, optional
        Pass True if you want to mutate `df` rather than getting an altered copy.
    **kwargs: keyword arguments for transform()
    """
    if not inplace:
        df = df.copy()

    param_cols = []
    if columns is None:
        columns = df.columns
    elif param2col is None:
        pass
    elif param2col.__class__ == dict:
        param_cols = list(param2col.values())
    else:
        param_cols = list(param2col)

    tmp_index = not df.index.is_unique
    if tmp_index:
        ix = df.index
        df.reset_index(drop=True, inplace=True)

    df.loc[:, columns] = transform(df[columns+param_cols], func, param2col, **kwargs)

    if tmp_index:
        df.index = ix

    if not inplace:
        return df



def transform_note_columns(df, to, note_cols=['chord_tones', 'added_tones', 'bass_note', 'root'], minor_col='localkey_is_minor', inplace=False, **kwargs):
    """ Turns columns with line-of-fifth tonal pitch classes into another representation.
        Uses: transform_columns()

    Parameters
    ----------
    df : :obj:`pandas.DataFrame`
        DataFrame where columns (or column combinations) work as function arguments.
    to : {'name', 'iv', 'pc', 'sd', 'rn'}
        The tone representation that you want to get from the `note_cols`.
        'name': Note names. Should only be used if the stacked fifths actually represent
                absolute tonal pitch classes rather than intervals over the local tonic.
                In other words, make sure to use 'name' only if 0 means C rather than I.
        'iv':   Intervals such that 0 = 'P1', 1 = 'P5', 4 = 'M3', -3 = 'm3', 6 = 'A4',
                -6 = 'D5' etc.
        'pc':   (Relative) chromatic pitch class, or distance from tonic in semitones.
        'sd':   Scale degrees such that 0 = '1', -1 = '4', -2 = 'b7' in major, '7' in minor etc.
                This representation requires a boolean column `minor_col` which is
                True in those rows where the stacks of fifths occur in a local minor
                context and False for the others. Alternatively, if all pitches are
                in the same mode or you simply want to express them as degrees of
                particular mode, you can pass the boolean keyword argument `minor`.
        'rn':   Roman numerals such that 0 = 'I', -2 = 'bVII' in major, 'VII' in minor etc.
                Requires boolean 'minor' values, see 'sd'.
    note_cols : :obj:`list`, optional
        List of columns that hold integers or collections of integers that represent
        stacks of fifth (0 = tonal center, 1 = fifth above, -1 = fourth above, etc).
    minor_col : :obj:`str`, optional
        If `to` is 'sd' or 'rn', specify a boolean column where the value is
        True in those rows where the stacks of fifths occur in a local minor
        context and False for the others.

    """
    transformations = {
        'name': fifths2name,
        'names': fifths2name,
        'iv': fifths2iv,
        'pc': fifths2pc,
        'sd': fifths2sd,
        'rn': fifths2rn,
    }
    assert to in transformations, "Parameter to needs to be one of {'name', 'iv', 'pc', 'sd', 'rn'}"
    cols = [col for col in note_cols if col in df.columns]
    if len(cols) < len(note_cols):
        logging.warning(f"Columns {[[col for col in note_cols if not col in df.columns]]}")
    param2col = None
    if to in ['sd', 'rn']:
        assert minor_col in df.columns or 'minor' in kwargs, f"'{to} representation requires a boolean column for the 'minor' argument, e.g. 'globalkey_is_minor'."
        if not 'minor' in kwargs:
            param2col = {'minor': minor_col}
    func = transformations[to]
    res = transform_columns(df, func, columns=note_cols, inplace=inplace, param2col=param2col, column_wise=True, **kwargs)
    if not inplace:
        return res



def transpose(e, n):
    """ Add `n` to all elements `e` recursively.
    """
    return map2elements(e, lambda x: x+n)



def transpose_changes(changes, old_num, new_num, old_minor=False, new_minor=False):
    """ Since the interval sizes expressed by the changes of the DCML harmony syntax
        depend on the numeral's position in the scale, these may change if the numeral
        is transposed. This function expresses the same changes for the new position.
        Chord tone alterations (of 3 and 5) stay untouched.
        Uses: changes2tpc()

    Parameters
    ----------
    changes : :obj:`str`
        A string of changes following the DCML harmony standard.
    old_num, new_num : :obj:`str`:
        Old numeral, new numeral.
    old_minor, new_minor : :obj:`bool`, optional
        For each numeral, pass True if it occurs in a minor context.
    """
    if pd.isnull(changes):
        return changes
    old = changes2tpc(changes, old_num, minor=old_minor, root_alterations=True)
    new = changes2tpc(changes, new_num, minor=new_minor, root_alterations=True)
    res = []
    get_acc = lambda n: n * '#' if n > 0 else -n * 'b'
    for (full, added, acc, chord_interval, iv1), (_, _, _, _, iv2) in zip(old, new):
        if iv1 is None or iv1 == iv2:
            res.append(full)
        else:
            d = iv2 - iv1
            if d % 7 > 0:
                logging.warning(f"The difference between the intervals of {full} in {old_num} and {new_num} (in {'minor' if minor else 'major'}) don't differ by chromatic semitones.")
            n_acc = acc.count('#') - acc.count('b')
            new_acc = get_acc(n_acc - d // 7)
            res.append(added + new_acc + chord_interval)
    return ''.join(res)
