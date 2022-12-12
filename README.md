<!-- TOC -->
* [The Annotated Mozart Sonatas: Score, Harmony, and Cadence](#the-annotated-mozart-sonatas--score-harmony-and-cadence)
  * [Changelog](#changelog)
    * [Version 2.0](#version-20)
      * [Changes to harmonize with other DCML corpora](#changes-to-harmonize-with-other-dcml-corpora)
      * [Changes to the content](#changes-to-the-content)
      * [Removed `mozart_loader.py`](#removed-mozartloaderpy)
  * [Getting the Data](#getting-the-data)
  * [Data Formats](#data-formats)
    * [Opening Scores](#opening-scores)
    * [Opening TSV files in a spreadsheet](#opening-tsv-files-in-a-spreadsheet)
    * [Loading TSV files in Python](#loading-tsv-files-in-python)
  * [How to read `metadata.tsv`](#how-to-read-metadatatsv)
    * [File information](#file-information)
    * [Composition information](#composition-information)
    * [Score information](#score-information)
    * [Identifiers](#identifiers)
  * [Generating all TSV files from the scores](#generating-all-tsv-files-from-the-scores)
  * [Questions, Suggestions, Corrections, Bug Reports](#questions-suggestions-corrections-bug-reports)
  * [License](#license)
* [Overview](#overview)
<!-- TOC -->

![Version](https://img.shields.io/github/v/release/DCMLab/mozart_piano_sonatas?display_name=tag)
[![DOI](https://zenodo.org/badge/249007132.svg)](https://zenodo.org/badge/latestdoi/249007132)
![GitHub repo size](https://img.shields.io/github/repo-size/DCMLab/mozart_piano_sonatas)
![GitHub all releases](https://img.shields.io/github/downloads/DCMLab/mozart_piano_sonatas/total?color=%252300&label=Downloaded%20ZIPs)
![License](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-9cf)

# The Annotated Mozart Sonatas: Score, Harmony, and Cadence

Scores, chord labels and cadence labels for Mozart's 18 piano sonatas, following
the [Neue Mozart Ausgabe](https://dme.mozarteum.at/DME/nma).

This dataset is accompanied by the data
report `Hentschel, J., Neuwirth, M. and Rohrmeier, M., 2021. The Annotated Mozart Sonatas: Score, Harmony, and Cadence. Transactions of the International Society for Music Information Retrieval, 4(1), pp.67–80. DOI:` [http://doi.org/10.5334/tismir.63](http://doi.org/10.5334/tismir.63)


## Changelog

### Version 2.0

#### Changes to harmonize with other DCML corpora

* Eenamed folder `scores`
  to `MS3` ([7549f6a](https://github.com/DCMLab/mozart_piano_sonatas/pull/5/commits/7549f6a68cd05e2bbce4a09f76a1821faf61aa4e))
* Extracted facets and metadata
  with [ms3 1.0.1](https://github.com/johentsch/ms3) ([9eb9fe3](https://github.com/DCMLab/mozart_piano_sonatas/pull/5/commits/9eb9fe3c26d5fbbdb61b485d6135dd421ed36dfd))
    * TSV files now come with the column `quarterbeats`, which measures in quarter notes each event's position as its
      distance from the beginning
    * The extracted harmony labels in the folder `harmonies` are expanded into feature columns by default.
    * Extracted notes now come with the columns `name` and `octave`.
    * Column `volta` (containing first and second endings) removed from pieces that don't have any.
    * `metadata.tsv` has been enriched with further columns, in particular information about each movement's dimensions,
      including dimensions upon unfolding repeats (for instance, `last_mn` has the number of
      measures, `last_mn_unfolded` the
      number of measures when playing all repeats)
    * The folder `reviewed` contains two files per movement:
        * A copy of the score where all out-of-label notes have been colored in red; additionally, modified labels (
          w.r.t. v1.0)
          are shown in these files in a diff-like manner (removed in red, added in green).
        * A copy of the harmonies TSV with six added columns that reflect the coloring of out-of-label notes ("coloring
          reports")
    * As long as the `ms3 review` has any complaints, it stores them in the file `warnings.log`. Currently, it is
      showing
      those labels where over 60% of the notes in the segment have been colored in red and probably need revisiting (
      Pull Requests welcome)
* Score updated
  using `ms3 update` ([13dfb6d](https://github.com/DCMLab/mozart_piano_sonatas/pull/5/commits/13dfb6d9a99c08a7f61b4fed195c36789a5d609d))
    * Files updated to MuseScore 3.6.2
    * All labels moved from the chord layer of staff 1 to the Roman Numeral Analysis layer of staff 2.
      This changes how they are displayed and eliminates the requirement to prepend
      a full stop to labels starting with a note name.
* Cadence labels now integrated with harmony labels as per
  [DCML harmony annotation standard 2.3.0](https://github.com/DCMLab/standards#v230) ([1c290e8](https://github.com/DCMLab/mozart_piano_sonatas/pull/5/commits/1c290e8981de37b91f03ba6e2eb7e5e2c8025186))
* TSV files are automatically kept up to date using
  the [dcml_corpus_workflow](https://github.com/DCMLab/dcml_corpus_workflow)
  ([c203595](https://github.com/DCMLab/mozart_piano_sonatas/pull/5/commits/c2035954476f1a8093999758008d9ea7d885a802))

#### Changes to the content

* Made phrase annotations consistent by adding missing curly
  brackets. ([9f10fc0](https://github.com/DCMLab/mozart_piano_sonatas/pull/5/commits/9f10fc03359a48f598f9d6b70a7b131ac8bd2510))
* Introduced first and second endings at the beginning of `K311-2` in order to introduce an `EC` label on the repetition
  of bar 1.
* Fixed repeat structure in _da capo_ movements K282-2 and K331-2 for correct unfolding
  ([b7271da](https://github.com/DCMLab/mozart_piano_sonatas/pull/5/commits/b7271da6ebd2e21abe7ccbe858065822a40095e7)..[0e9f060](https://github.com/DCMLab/mozart_piano_sonatas/pull/5/commits/0e9f060dbfb1c4143362d586e30a3e309dcdbeeb))
* updated labels of
  K283-3 ([f1fe032](https://github.com/DCMLab/mozart_piano_sonatas/pull/5/commits/f1fe0321616039ce77aad55914eac1640fed2255))
* corrected scores in a few
  places ([b6aa4f1](https://github.com/DCMLab/mozart_piano_sonatas/pull/5/commits/b6aa4f1cd271ef475e559b53bbcb5fc4834040b6),
  [438acb0](https://github.com/DCMLab/mozart_piano_sonatas/pull/5/commits/438acb0da8e2f2203d73e313af0d14c03e0f18c2))

#### Removed `mozart_loader.py`

The functionality of the loader has been superseded by the [ms3 parsing library](https://github.com/johentsch/ms3).
Once installed (`pip install ms3`), you'll have several commands on your hands, one of which is `ms3 transform`. For
example, head to the folder with the dataset and type `ms3 transform -N` to create the concatenated note list.
`ms3 transform -h` will show all options.


## Getting the Data

First, create a local copy of this repository, either by using the command 

```bash
git clone https://github.com/DCMLab/mozart_piano_sonatas.git
```

or by unpacking this [ZIP file](https://github.com/DCMLab/dcml_corpora/archive/refs/heads/main.zip). 



## Data Formats

Every sonata movement is represented by five files with identical filenames in five different folders. For example, the
first movement of the first sonata K. 279 has the following files:

* `MS3/K279-1.mscx`: Uncompressed MuseScore file including the music and harmony labels.
* `notes/K279-1.tsv`: A table of all note heads contained in the score and their relevant features (not each of them represents an onset, some are tied together)
* `measures/K279-1.tsv`: A table with relevant information about the measures in the score.
* `harmonies/K279-1.tsv`: A list of the included harmony labels (including cadences and phrases) with their positions in
  the score.

### Opening Scores

After navigating to your local copy, you can open the scores in the folder `MS3` with the free and open source score
editor [MuseScore](https://musescore.org).

### Opening TSV files in a spreadsheet

Tab-separated value (TSV) files are like Comma-separated value (CSV) files and can be opened with most modern text
editors. However, for correctly displaying the columns, you might want to use a spreadsheet or an addon for your
favourite text editor. When you use a spreadsheet such as Excel, it might annoy you by interpreting fractions as
dates. This can be circumvented by using `Data --> From Text/CSV` or the free alternative
[LibreOffice Calc](https://www.libreoffice.org/download/download/). Other than that, TSV data can be loaded with
every modern programming language.

### Loading TSV files in Python

Since the TSV files contain null values, lists, fractions, and numbers that are to be treated as strings, you may want
to use this code to load any TSV files related to this repository (provided you're doing it in Python). After a quick
`pip install -U ms3` (requires Python 3.10) you'll be able to load any TSV like this:

```python
import ms3

labels = ms3.load_tsv('harmonies/K283-1.tsv')
notes = ms3.load_tsv('notes/K283-1.tsv')
```

## How to read `metadata.tsv`

This section explains the meaning of the columns contained in `metadata.tsv`.

### File information

| column                 | content                                                    |
|------------------------|------------------------------------------------------------|
| **fname**              | name without extension (for referencing related files)     |
| **rel_path**           | relative file path of the score, including extension       |
| **subdirectory**       | folder where the score is located                          |    
| **last_mn**            | last measure number                                        |
| **last_mn_unfolded**   | number of measures when playing all repeats                |
| **length_qb**          | length of the piece, measured in quarter notes             |
| **length_qb_unfolded** | length of the piece when playing all repeats               |
| **volta_mcs**          | measure counts of first and second endings                 |
| **all_notes_qb**       | summed up duration of all notes, measured in quarter notes |
| **n_onsets**           | number of note onsets                                      |
| **n_onset_positions**  | number of unique not onsets ("slices")                     |


### Composition information

| column             | content                   |
|--------------------|---------------------------|
| **composer**       | composer name             |
| **workTitle**      | full sonata title         |
| **composed_start** | earliest composition date |
| **composed_end**   | latest composition date   |
| **workNumber**     | Köchel number             |
| **movementNumber** | 1, 2, or 3                |
| **movementTitle**  | title of the movement     |

### Score information

| column          | content                                                |
|-----------------|--------------------------------------------------------|
| **label_count** | number of chord labels                                 |
| **KeySig**      | key signature(s) (negative = flats, positive = sharps) |
| **TimeSig**     | time signature(s)                                      |
| **musescore**   | MuseScore version                                      |
| **source**      | URL to the first typesetter's file                     |
| **typesetter**  | first typesetter                                       |
| **annotator**   | creator of the chord labels                            |
| **reviewers**   | reviewers of the chord labels                          |

### Identifiers

These columns provide a mapping between multiple identifiers for the sonatas (not for individual movements).

| column          | content                                                                                                 |
|-----------------|---------------------------------------------------------------------------------------------------------|
| **wikidata**    | URL of the [WikiData](https://www.wikidata.org/) item                                                   |
| **viaf**        | URL of the Virtual International Authority File ([VIAF](http://viaf.org/)) entry                        |
| **musicbrainz** | [MusicBrainz](https://musicbrainz.org/) identifier                                                      |
| **imslp**       | URL to the wiki page within the International Music Score Library Project ([IMSLP](https://imslp.org/)) |


## Generating all TSV files from the scores

When you have made changes to the scores and want to update the TSV files accordingly, you can use the following
command (provided you have pip-installed [ms3](https://github.com/johentsch/ms3)):

```python
ms3 extract -M -N -X -D # for measures, notes, expanded annotations, and metadata
```

If, in addition, you want to generate the reviewed scores with out-of-label notes colored in red, you can do

```python
ms3 review -M -N -X -D # for extracting measures, notes, expanded annotations, and metadata
```

By adding the flag `-c` to the review command, it will additionally compare the (potentially modified) annotations in the score
with the ones currently present in the harmonies TSV files and reflect the comparison in the reviewed scores.

## Questions, Suggestions, Corrections, Bug Reports

Please create an issue and feel free to fork and submit pull requests.

## License

Creative Commons Attribution-NonCommercial-ShareAlike 4.0 ([CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/))

# Overview

| file_name | measures | labels | annotators   | reviewers                           |
|-----------|---------:|-------:|--------------|-------------------------------------|
| K279-1    |      100 |    251 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K279-2    |       74 |    156 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K279-3    |      158 |    321 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K280-1    |      144 |    225 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K280-2    |       60 |    124 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K280-3    |      190 |    199 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K281-1    |      109 |    208 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K281-2    |      106 |    153 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K281-3    |      162 |    384 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K282-1    |       36 |    104 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K282-2    |       72 |    129 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K282-3    |      102 |    176 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K283-1    |      120 |    326 | Tal Soker    | Johannes Hentschel, Markus Neuwirth |
| K283-2    |       39 |    169 | Tal Soker    | Johannes Hentschel, Markus Neuwirth |
| K283-3    |      277 |    337 | Tal Soker    | Johannes Hentschel, Markus Neuwirth |
| K284-1    |      127 |    330 | Tal Soker    | Johannes Hentschel, Markus Neuwirth |
| K284-2    |       92 |    228 | Tal Soker    | Johannes Hentschel, Markus Neuwirth |
| K284-3    |      260 |    755 | Adrian Nagel | Johannes Hentschel, Markus Neuwirth |
| K309-1    |      155 |    307 | Tal Soker    | Johannes Hentschel, Markus Neuwirth |
| K309-2    |       79 |    259 | Tal Soker    | Johannes Hentschel, Markus Neuwirth |
| K309-3    |      252 |    406 | Tal Soker    | Johannes Hentschel, Markus Neuwirth |
| K310-1    |      133 |    292 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K310-2    |       86 |    252 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K310-3    |      252 |    428 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K311-1    |      112 |    319 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K311-2    |       93 |    241 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K311-3    |      269 |    491 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K330-1    |      150 |    293 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K330-2    |       64 |    187 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K330-3    |      171 |    365 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K331-1    |      134 |    399 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K331-2    |      100 |    160 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K331-3    |      127 |    128 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K332-1    |      229 |    316 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K332-2    |       40 |    168 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K332-3    |      245 |    449 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K333-1    |      165 |    431 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K333-2    |       82 |    217 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K333-3    |      224 |    460 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K457-1    |      185 |    308 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K457-2    |       57 |    214 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K457-3    |      319 |    328 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K533-1    |      239 |    584 | Adrian Nagel | Johannes Hentschel, Markus Neuwirth |
| K533-2    |      122 |    261 | Adrian Nagel | Johannes Hentschel, Markus Neuwirth |
| K533-3    |      187 |    423 | Adrian Nagel | Johannes Hentschel, Markus Neuwirth |
| K545-1    |       73 |    119 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K545-2    |       74 |    146 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K545-3    |       73 |    143 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K570-1    |      209 |    245 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K570-2    |       55 |    250 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K570-3    |       89 |    281 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K576-1    |      160 |    295 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K576-2    |       67 |    151 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |
| K576-3    |      189 |    381 | Uli Kneisel  | Johannes Hentschel, Markus Neuwirth |

*Overview table updated using [ms3](https://johentsch.github.io/ms3/) 1.0.1.*
