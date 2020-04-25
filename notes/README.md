## Columns

| column | type | description |
|----------------------|----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **mc** | integer | Measure count, identifier for the measure units in the XML encoding. |
| **mn** | integer | Measure number, continuous count of complete measures as used in printed editions. |
| **playthrough** | integer | (with `[-u]`) For the unfolded representations, a running count of complete measures disambiguating repeated MNs.   |
| **timesig** | string | (with `[-e][-E]`) Time signature of the measure in which the note occurs. |
| **beat** | fraction | (with `[-e][-E]`) On which beat the note occurs, expressed as string. Downbeat positions are just integers (e.g. `'1'`) and upbeat positions have a fraction of the respective beat size attached, for instance, in `2/2` meter, beat `'1.1/2'` is on the second quarter note and beat `'1.1/3'` is on the second quarter triplet note.<br> The mapping timesig => beat size is `'2/2' => 1/2, '4/4' => 1/4, '2/4' => 1/4, '3/8' => 1/8, '6/8' => 3/8`} |
| **onset** | fraction | Note's temporal position from beat 1 of the measure, expressed in fractions of a whole note (1/4 = quarter note, 1/12 = triplet eigth, etc.) |
| **duration** | fraction | Note's duration without taking into account notes tied to it. Expressed in fractions of a whole note. |
| **gracenote** | string | For grace notes, type of the grace note as encoded in the MuseScore source code (duration = 0). |
| **nominal_duration** | fraction | Note duration without taking into account dots or tuplets. |
| **scalar** | fraction | Multiplier resulting from dots and tuplets. `scalar` * `nominal_duration` = `duration` |
| **tied** | Int64 | Encodes ties on the note's left (`-1`), on its right (`1`) or both (`0`). A tie merges a note with an adjacent one having the same pitch.<br>`<NA>`: No ties. This note represents an onset and ends after the given duration.<br>`1`: This note is tied to the next one. It represents an onset but not a note ending.<br>`0`: This note is being tied to *and* tied to the next one. It does not represent an onset, nor a note ending.<br>`-1`: This note is being tied to. That is, it does not represent an onset, instead it adds to the duration of a previous note on the same pitch and ends it.<br>In case the ties are merged via the parameter `-T`, only `1` remains, `-1` and `0` are dropped and the durations merged. |
| **tpc** | integer | Tonal Pitch Class. Encodes note names by their position on the line of fifth with `0` = C, `1` = G, `2` = D, `-1` = F, `-2` = `Bb` etc. The octave is defined by `midi DIV 12 - 1` |
| **midi** | integer | MIDI pitch with `60` = C4, `61` = C#4/Db4/B##3 etc. |
| **staff** | integer | In which staff the note occurs. `1` = upper staff. |
| **voice** | integer | In which notational layer the note occurs. `1` = upper layer. |
| **volta** | Int64 | Disambiguates first and second endings (or more). Voltas constitute different versions of the same `mn`. This column can be expected to have the values `<NA>`, `1` and `2`. |
