## Columns

The TSVs in this folder each contain all notes of one of the movements with their temporal positions and other features. The column `presence` shows with which parameters of `mozart_loader.py` the column is present, where `raw` means that the column is present in the raw data and will be output with `-N`. The note lists mostly keep the same representation as in the raw data, except for added columns for time signature and beat representation of note onsets when using `mozart_loader.py [-e][-E][-g][-a][-A]`.

The data type `Int64` stands for integer columns containing NULL values.

| column | type | presence | description |
|----------------------|----------|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **mc** | integer | raw | Measure count, identifier for the measure units in the XML encoding. Always starts with 1 for correspondence to MuseScore's status bar. |
| **mn** | integer | raw | Measure number, continuous count of complete measures as used in printed editions. Starts with 1 except for pieces beginning with a pickup measure, numbered as 0. |
| **playthrough** | integer | u | For the unfolded representations, a running count of complete measures disambiguating repeated MNs. |
| **timesig** | string | e/E/g/a/A | Time signature of the measure in which the note occurs. |
| **beat** | fraction | e/E/g/a/A | On which beat the note occurs, expressed as string. Downbeat positions are just integers (e.g. `'1'`) and upbeat positions have a fraction of the respective beat size attached, for instance, in `2/2` meter, beat `'1.1/2'` is on the second quarter note and beat `'1.1/3'` is on the second quarter triplet note.<br> The mapping timesig => beat size is `'2/2' => 1/2, '4/4' => 1/4, '2/4' => 1/4, '3/8' => 1/8, '6/8' => 3/8`} |
| **onset** | fraction | raw | Note's temporal position from beat 1 of the measure, expressed in fractions of a whole note (1/4 = quarter note, 1/12 = triplet eigth, etc.) |
| **duration** | fraction | raw | Note's duration without taking into account notes tied to it. Expressed in fractions of a whole note. |
| **gracenote** | string | raw | For grace notes, type of the grace note as encoded in the MuseScore source code (duration = 0). |
| **nominal_duration** | fraction | raw | Note duration without taking into account dots or tuplets. |
| **scalar** | fraction | raw | Multiplier resulting from dots and tuplets. `scalar` * `nominal_duration` = `duration` |
| **tied** | Int64 | raw | Encodes ties on the note's left (`-1`), on its right (`1`) or both (`0`). A tie merges a note with an adjacent one having the same pitch.<br>`<NA>`: No ties. This note represents an onset and ends after the given duration.<br>`1`: This note is tied to the next one. It represents an onset but not a note ending.<br>`0`: This note is being tied to *and* tied to the next one. It does not represent an onset, nor a note ending.<br>`-1`: This note is being tied to. That is, it does not represent an onset, instead it adds to the duration of a previous note on the same pitch and ends it.<br>In case the ties are merged via the parameter `-T`, only `1` remains, `-1` and `0` are dropped and the durations merged. |
| **tpc** | integer | raw | Tonal Pitch Class. Encodes note names by their position on the line of fifth with `0` = C, `1` = G, `2` = D, `-1` = F, `-2` = `Bb` etc. The octave is defined by `midi DIV 12 - 1` |
| **midi** | integer | raw | MIDI pitch with `60` = C4, `61` = C#4/Db4/B##3 etc. |
| **staff** | integer | raw | In which staff the note occurs. `1` = upper staff. |
| **voice** | integer | raw | In which notational layer the note occurs. `1` = upper layer. |
| **volta** | Int64 | raw **only** | Disambiguates endings: `1` for first endings, `2` for second endings. This column is present only for disambiguation in the raw data because `mozart_loader.py` has been designed to correctly deal with first and second endings by deleting first endings or unfolding repetitions (parameter `-u`). |
