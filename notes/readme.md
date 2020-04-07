## Columns

* **mc**: Measure count, identifier for the measure units in the XML encoding.
* **mn**: Measure number, continuous count of complete measures as used in printed editions.
* **onset**: Note's temporal position from beat 1 of the measure, expressed in fractions of a whole note (1/4 = quarter note, 1/12 = triplet eigth, etc.)
* **duration**: Note's duration without taking into account notes tied to it. Expressed in fractions of a whole note.
* **gracenote**: For grace notes, type of the grace note (duration = 0).
* **nominal_duration**: Note duration without taking into account dots or tuplets.
* **scalar**: Multiplier resulting from dots and tuplets. `scalar` * `nominal_duration` = `duration`
* **tied**: Encodes ties on the note's left (`-1`), on its right (`1`) or both (`0`). A tie merges a note with an adjacent one having the same pitch.
  * `<NA>`: No ties. This note represents an onset and ends after the given duration.
  * `-1`: This note is being tied to. That is, it does not represent an onset, instead it adds to the duration of a previous note on the same pitch and ends it.
  * `0`: This note is being tied to *and* tied to the next one. It does not represent an onset, nor a note ending.
  * `1`: This note is tied to the next one. It represents an onset but not a note ending.
* **tpc**: Tonal Pitch Class. Encodes note names by their position on the line of fifth with `0` = C, `1` = G, `2` = D, `-1` = F, `-2` = `Bb` etc. The octave is defined by `midi DIV 12 - 1`
* **midi**: MIDI pitch with `60` = C4, `61` = C#4/Db4/B##3 etc.
* **staff**: In which staff the note occurs. `1` = upper staff.
* **voice**: In which notational layer the note occurs. `1` = upper layer.
* **volta**: Disambiguates first and second endings (or more). Voltas constitute different versions of the same `mn`. This column can be expected to have the values `<NA>`, `1` and `2`.
