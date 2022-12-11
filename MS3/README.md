# Scores

These uncompressed [MuseScore 3](https://musescore.org/download) files have been originally typeset by [Lucas Mossman](https://musescore.com/lukemossman), [Craig Stuart Sapp](https://github.com/craigsapp/mozart-piano-sonatas), [Tobias Schölkopf](http://www.tobis-notenarchiv.de/mozart/index.htm), and Tom Schreyer. Later, they have been corrected by professional collaborators at [www.tunescribers.com](https://www.tunescribers.com/) to conform to the [Neue Mozart Ausgabe](https://dme.mozarteum.at/DME/nma) content-wise (not layout-wise).

The precise metadata can be found in `metadata.tsv`. Thanks to Johannes Rüther for help with compiling them.

## Ambiguous Measure Numbers

The folder `ambiguous_measure_numbers` contains alternative scores of four files. The difference is that in these scores, the bar numbering follows the Neue Mozart Ausgabe (NMA) and restarts at section breaks later in the piece. These are the only cases where the bar numbering in the main folder deviates: For unambiguous referencing, continuous bar numbers were used. However, we are joining the versions with the original NMA numbering for the sake of completeness:

* ambiguous_measure_numbers_for_K282-2.mscx (Menuetto I & II)
* ambiguous_measure_numbers_for_K284-3.mscx (Variations)
* ambiguous_measure_numbers_for_K331-1.mscx (Variations)
* ambiguous_measure_numbers_for_K331-2.mscx (Menuetto & Trio)


These files are not listed in `metadata.tsv`.


## Metadata Columns

This section explains the meaning of the columns contained in `metadata.tsv`.

### File information

| column        | content                                                |
|---------------|--------------------------------------------------------|
| **path**      | relative path of the file                              |
| **filename**  | name without extension (for referencing related files) |
| **extension** | file extension (.mscx)                                 |
| **md5**       | MD5 checksum                                           |

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
