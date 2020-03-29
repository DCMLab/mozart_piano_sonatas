import argparse, os, sys
from fractions import Fraction as frac
from functools import reduce
try:
    import pandas as pd
except ImportError:
    sys.exit("""This script requires the pandas package. You can install it using the command
python -m pip install pandas""")


os.environ['NUMEXPR_MAX_THREADS'] = '64' # to silence NumExpr prompt
idx = pd.IndexSlice                      # for easy MultiIndex slicing

CONVERTERS = {
    'onset': frac,
    'duration': frac,
    'nominal_duration': frac,
    'scalar': frac,}

DTYPES = {
    'mc': int,
    'mn': int,
    'tied': 'Int64',
    'tpc': int,
    'midi': int,
    'staff': int,
    'voice': int,
    'volta': 'Int64',
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

# def pair2list(pair):
#     """Takes a range such as (2,4) and turns it into the corresponding list [2,3,4]"""
#     fr, to = pair
#     fr, to = int(fr), int(to)
#     if to < fr:
#         fr, to = to, fr
#     if fr < 1:
#         fr = 1
#     if to > 18:
#         to = 18
#     return list(range(fr, to+1))
#
# def treatval(val):
#     """ Turns a parameter into a list of int."""
#     try:
#         val = [int(val)]
#     except:
#         if val.__class__ == tuple and len(sonatas) == 2:
#             val = pair2list(val)
#     return [int(i) for i in val if 0 < int(i) < 19]





def read_tsvs(dir, selection):
    files = (selection.filename + '.tsv').values
    return pd.concat([pd.read_csv(os.path.join(dir, f), sep='\t', dtype=DTYPES, converters=CONVERTERS) for f in files],
                     keys=selection.filename)




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



def select_files(sonatas=None, movements=None):
    """

    """
    if sonatas is None:
        df = FILE_LIST
    else:
        df = FILE_LIST.loc[sonatas]
    if movements is not None:
        df = df.loc[idx[:, movements],]
    return df



def store_result(df, fname, what):
    tsv_name = f"{fname}_{what}.tsv" if what != 'joined' else fname + '.tsv'
    tsv_path = os.path.join(args.dir, tsv_name)
    df.to_csv(tsv_path, sep='\t')
    print(f"PREVIEW of {tsv_path}:", notes.head(1), sep='\n', end='\n\n')



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description = '''\
------------------------------------
| Format Mozart data to your needs |
------------------------------------

Run this script at the top level of (your local copy of) the repo  mozart_piano_sonatas.
''')
    parser.add_argument('name', metavar='NAME', nargs='?', type=check_dir, help='You may choose a name for the new TSV file(s). Existing files will be overwritten.')
    parser.add_argument('dir', metavar='DIR', nargs='?', type=check_dir, default=os.path.join(os.getcwd(), 'formatted'), help='Folder for storing the new TSV file(s). Can be relative, defaults to ./formatted')
    parser.add_argument('-s','--sonatas', nargs='+', type=int, help="Select sonatas out of 1-18, e.g. -s 2 5 12")
    parser.add_argument('-m','--movements', nargs='+', type=int, help="Select only movements 1, 2 or 3, e.g. -m 1 3")
    parser.add_argument('-t','--test', action='store_true', help="Only test/view file selection without storing any data. Use -t without -sm to view all files.")
    parser.add_argument('-H','--harmonies', action='store_true', help="Get chord labels.")
    parser.add_argument('-C','--cadences', action='store_true', help="Get cadence labels.")
    parser.add_argument('-N','--notes', action='store_true', help="Get note lists.")
    parser.add_argument('-j','--join', action='store_true', help="Join the data into one single TSV.")
    parser.add_argument('-p','--propagate', action='store_true', help="When joining, spread out chord and cadence labels.")
    args = parser.parse_args()

    selection = select_files(sonatas=args.sonatas, movements=args.movements)
    if not args.harmonies and not args.cadences and not args.notes:
        print("Select the kind of data: -N for notes, -H for harmony labels, and -C for cadence labels. Pass -j to join several kinds into a single TSV.")
    elif len(selection) == 0:
        print("No data matching your selection.")
    elif args.test:
        print(selection)
    else:
        fname = ' '.join(sys.argv[1:]) if args.name is None else args.name
        script_path = os.path.realpath(os.path.dirname(__file__))
        if args.join:
            joining = []
            assert sum([args.notes, args.harmonies, args.cadences]) > 1, "Select at least two kinds of data for joining."

        if args.notes:
            notes = read_tsvs(os.path.join(script_path, 'labels/notes'), selection)
            if args.join:
                joining.append(notes.set_index(['mn', 'onset'], append=True))
            else:
                store_result(notes, fname, 'notes')

        if args.harmonies:
            chords = read_tsvs(os.path.join(script_path, 'labels/chords'), selection)
            if not args.join:
                store_result(chords, fname, 'chords')
            else:
                joining.append(chords.set_index(['mn', 'onset'], append=True))

        if args.cadences:
            cadences = read_tsvs(os.path.join(script_path, 'labels/cadences'), selection)
            if not args.join:
                store_result(cadences, fname, 'cadences')
            else:
                joining.append(cadences.set_index(['mn', 'onset'], append=True))

        if args.join:
            for df in joining:
                df.index = df.index.droplevel(1)
            joined = reduce(lambda left,right: pd.merge(left, right, left_index=True, right_index=True, how='outer', suffixes=('', '_y')), joining)
            duplicates = [col for col in joined.columns if col.endswith('_y')]
            joined.drop(columns=duplicates, inplace=True)
            if args.propagate:
                if args.cadences:
                    joined.cadence.fillna(method='bfill', inplace=True)
                if args.notes and args.harmonies:
                    joined.chords.fillna(method='ffill', inplace=True)
            store_result(joined, fname, 'joined')
