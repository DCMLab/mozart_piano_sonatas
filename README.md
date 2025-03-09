![Version](https://img.shields.io/github/v/release/DCMLab/mozart_piano_sonatas?display_name=tag)
[![DOI](https://zenodo.org/badge/249007132.svg)](https://doi.org/10.5281/zenodo.7424962)
![GitHub repo size](https://img.shields.io/github/repo-size/DCMLab/mozart_piano_sonatas)
![License](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-9cf)


This is a README file for a data repository originating from the [DCML corpus initiative](https://github.com/DCMLab/dcml_corpora)
and serves as welcome page for both 

* the GitHub repo [https://github.com/DCMLab/mozart_piano_sonatas](https://github.com/DCMLab/mozart_piano_sonatas) and the corresponding
* documentation page [https://dcmlab.github.io/mozart_piano_sonatas](https://dcmlab.github.io/mozart_piano_sonatas)

For information on how to obtain and use the dataset, please refer to [this documentation page](https://dcmlab.github.io/mozart_piano_sonatas/introduction).

# The Annotated Mozart Sonatas: Score, Harmony, and Cadence (A corpus of annotated scores)

Scores, chord labels and cadence labels for Mozart's 18 piano sonatas, following
the [Neue Mozart Ausgabe](https://dme.mozarteum.at/DME/nma).

## Getting the data

* download repository as a [ZIP file](https://github.com/DCMLab/mozart_piano_sonatas/archive/main.zip)
* download a [Frictionless Datapackage](https://specs.frictionlessdata.io/data-package/) that includes concatenations
  of the TSV files in the four folders (`measures`, `notes`, `chords`, and `harmonies`) and a JSON descriptor:
  * [mozart_piano_sonatas.zip](https://github.com/DCMLab/mozart_piano_sonatas/releases/latest/download/mozart_piano_sonatas.zip)
  * [mozart_piano_sonatas.datapackage.json](https://github.com/DCMLab/mozart_piano_sonatas/releases/latest/download/mozart_piano_sonatas.datapackage.json)
* clone the repo: `git clone https://github.com/DCMLab/mozart_piano_sonatas.git` 


## Data Formats

Each piece in this corpus is represented by five files with identical name prefixes, each in its own folder. 
For example, the first movement of the first sonata, K. 279 has the following files:

* `MS3/K279-1.mscx`: Uncompressed MuseScore 3.6.2 file including the music and annotation labels.
* `notes/K279-1.notes.tsv`: A table of all note heads contained in the score and their relevant features (not each of them represents an onset, some are tied together)
* `measures/K279-1.measures.tsv`: A table with relevant information about the measures in the score.
* `chords/K279-1.chords.tsv`: A table containing layer-wise unique onset positions with the musical markup (such as dynamics, articulation, lyrics, figured bass, etc.).
* `harmonies/K279-1.harmonies.tsv`: A table of the included harmony labels (including cadences and phrases) with their positions in the score.

Each TSV file comes with its own JSON descriptor that describes the meanings and datatypes of the columns ("fields") it contains,
follows the [Frictionless specification](https://specs.frictionlessdata.io/tabular-data-resource/),
and can be used to validate and correctly load the described file. 

### Opening Scores

After navigating to your local copy, you can open the scores in the folder `MS3` with the free and open source score
editor [MuseScore](https://musescore.org). Please note that the scores have been edited, annotated and tested with
[MuseScore 3.6.2](https://github.com/musescore/MuseScore/releases/tag/v3.6.2). 
MuseScore 4 has since been released which renders them correctly but cannot store them back in the same format.

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
`pip install -U ms3` (requires Python 3.10 or later) you'll be able to load any TSV like this:

```python
import ms3

labels = ms3.load_tsv("harmonies/K279-1.harmonies.tsv")
notes = ms3.load_tsv("notes/K279-1.notes.tsv")
```


## Version history

See the [GitHub releases](https://github.com/DCMLab/mozart_piano_sonatas/releases).

## Questions, Suggestions, Corrections, Bug Reports

Please [create an issue](https://github.com/DCMLab/mozart_piano_sonatas/issues) and/or feel free to fork and submit pull requests.

## Cite as

> Hentschel, J., Neuwirth, M., & Rohrmeier, M. (2021). The Annotated Mozart Sonatas: Score, harmony, and cadence. Transactions of the International Society for Music Information Retrieval, 4(1), 67–80. https://doi.org/10.5334/tismir.63

## License

Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License ([CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)).

![cc-by-nc-sa-image](https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png)

## Overview
|file_name|measures|labels| annotators |             reviewers             |
|---------|-------:|-----:|------------|-----------------------------------|
|K279-1   |     100|   251|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K279-2   |      74|   156|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K279-3   |     158|   321|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K280-1   |     144|   225|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K280-2   |      60|   124|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K280-3   |     190|   199|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K281-1   |     109|   208|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K281-2   |     106|   153|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K281-3   |     162|   384|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K282-1   |      36|   104|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K282-2   |      72|   129|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K282-3   |     102|   176|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K283-1   |     120|   326|Tal Soker   |Johannes Hentschel, Markus Neuwirth|
|K283-2   |      39|   169|Tal Soker   |Johannes Hentschel, Markus Neuwirth|
|K283-3   |     277|   337|Tal Soker   |Johannes Hentschel, Markus Neuwirth|
|K284-1   |     127|   330|Tal Soker   |Johannes Hentschel, Markus Neuwirth|
|K284-2   |      92|   228|Tal Soker   |Johannes Hentschel, Markus Neuwirth|
|K284-3   |     260|   755|Adrian Nagel|Johannes Hentschel, Markus Neuwirth|
|K309-1   |     155|   307|Tal Soker   |Johannes Hentschel, Markus Neuwirth|
|K309-2   |      79|   259|Tal Soker   |Johannes Hentschel, Markus Neuwirth|
|K309-3   |     252|   406|Tal Soker   |Johannes Hentschel, Markus Neuwirth|
|K310-1   |     133|   292|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K310-2   |      86|   252|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K310-3   |     252|   428|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K311-1   |     112|   319|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K311-2   |      93|   241|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K311-3   |     269|   491|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K330-1   |     150|   293|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K330-2   |      64|   187|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K330-3   |     171|   365|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K331-1   |     134|   399|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K331-2   |     100|   160|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K331-3   |     127|   128|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K332-1   |     229|   316|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K332-2   |      40|   168|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K332-3   |     245|   449|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K333-1   |     165|   431|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K333-2   |      82|   217|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K333-3   |     224|   460|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K457-1   |     185|   308|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K457-2   |      57|   214|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K457-3   |     319|   328|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K533-1   |     239|   584|Adrian Nagel|Johannes Hentschel, Markus Neuwirth|
|K533-2   |     122|   261|Adrian Nagel|Johannes Hentschel, Markus Neuwirth|
|K533-3   |     187|   423|Adrian Nagel|Johannes Hentschel, Markus Neuwirth|
|K545-1   |      73|   119|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K545-2   |      74|   146|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K545-3   |      73|   143|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K570-1   |     209|   245|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K570-2   |      55|   250|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K570-3   |      89|   281|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K576-1   |     160|   295|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K576-2   |      67|   151|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|
|K576-3   |     189|   381|Uli Kneisel |Johannes Hentschel, Markus Neuwirth|


*Overview table automatically updated using [ms3](https://ms3.readthedocs.io/).*
