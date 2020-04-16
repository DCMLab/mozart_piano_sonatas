# mozart_piano_sonatas
Chord and cadence labels for Mozart's 18 piano sonatas

# Data Formats

Every sonata movement is represented by five files with identical filenames in five different folders. For example, the first movement of the first sonata K. 279 has the following files:

* `scores/K279-1.mscx`: Uncompressed MuseScore file including the music and harmony labels.
* `notes/K279-1.tsv`: A table of all notes contained in the score and their relevant features.
* `measures/K279-1.tsv`: A table with relevant information about the measures in the score.
* `harmonies/K279-1.tsv`: A list of the included harmony labels with their positions in the score.
* `cadences/K279-1.tsv`: A list of cadence labels and their positions.

The READMEs in the respective folders contain information about the features included in the TSV files.

# Accessing the Data

The included script `mozart_loader.py` lets you conveniently create an augmented representation of the data. First, create a local copy of this repository, either by using the command `git clone https://github.com/DCMLab/mozart_piano_sonatas.git` or by unpacking this [ZIP file](https://github.com/DCMLab/mozart_piano_sonatas/archive/master.zip). After navigating to your local copy, you can simply run the script by typing `python mozart_loader.py`. The script requires Python >= 3.6 with the `pandas` library installed.

## Raw Data

> Run `python mozart_loader.py -h` to see the overview of available options.

The script's most simple functionality concatenates all TSV files from the folders and stores them as single files:

* `-N` concatenates the note matrices
* `-M` concatenates the measure matrices
* `-H` concatenates the harmony labels
* `-C` concatenates the cadence labels

In case you want to join harmony labels with notes and/or cadence labels in a single file, add `-j` for joining. The basic representation of all data in a single file is yielded by `python mozart_loader.py -NHCj` (Measure lists are not joined, they are more of an auxiliary character and would still be output as a separate file.)

When joining the notes with labels, the latter often appear duplicated, namely once for every note with the identical onset. All notes that do not coincide with a label have `NaN` values in the concerning columns. This can be circumvented using the parameter `-p` which propagates the labels (and their features), thus identifying all notes that fall in their range.

## Accessing Harmony Features

The harmony labels follow the [DCML standard for harmonic annotation](https://github.com/DCMLab/standards) and can be split into feature columns.

* Using the option `-e` on the script will perform this expansion for you and spread the encoded information over the DataFrame, e.g. information about global and local keys.
* If you want to transpose all labels to the global tonic, thus eliminating the information about local keys, use `-g`.
* The chord tones expressed by the labels can be additionally computed by using `-E` instead of `-e`. They are expressed as integer intervals representing the count of perfect fifths you need to stack on the tonic, i.e., `0` is the tonic, `1` the dominant, `2` the supertonic, `-1` the subdominant, etc.
  * If the parameter `-g` is set, all chord tones are expressed as intervals (stacks of fifths) over the *global* tonic.
  * Otherwise, they represent intervals (stacks of fifths) over the chord's *local* tonic.
  * Or you can have all chord tones represent absolute pitches, based on the global key. In that case they display intervals (stacks of fifths) over the tone C = `0`, making G = `1`, F = `-1` etc.

All options can be combined with the above-mentioned functionality for data joining. The thickest data representation would be yielded using `python mozart_loader.py NHCEjp`. Except if you add:

## Repetitions

By default, all data is being returned as though playing every section only once, i.e. without first endings (without *prima volta*). Instead, you may choose the 'unfolded' version that duplicates notes and labels depending on the piece's repeat structure. Simply add `-u` to the parameters. This puts first and second endings in their correct positions, thus creating correct transitions and event counts that are closer to what is actually being performed.
