## Columns
* **mc**: Measure count, identifier for the measure units in the XML encoding.
* **mn**: Measure number, continuous count of complete measures as used in printed editions.
* **keysig**: Key signature as the amount of accidentals. Sharps as positive, flats as negative integers. `1` = G major / E minor; `-1` = F major / D minor
* **timesig**: Time signature of the complete measure (`mn`). Treat as string.
* **act_dur**: Actual duration of the `mc` expressed as fraction of a whole note (`1/4` = quarter note).
* **offset**: Distance of `mc` from beat 1 of the corresponding complete measure `mn`, expressed as fraction of a whole note.
* **voices**: Number of notational layers occurring in this `mc`.
* **repeats**: Repeat signs and/or indicators for the first and the last measure. Serves to compute the repeat structure.
* **volta**: Disambiguates first and second endings (or more). Voltas constitute different versions of the same mn. This column can be expected to have the values <NA>, 1 and 2.
* **barline**: Barline style on the right of the `mc`.
* **numbering_offset**: Number to be added to this and all subsequent `mn`s, determined by the "Add to bar number" functionality in MuseScore.
* **dont_count**: If `1`, this `mc` is not counted as the next `mn`. Otherwise `<NA>` Determined by the "Exclude from bar count" functionality in MuseScore.
* **next**: One or several `mc`s that can follow this `mc`. If there are several measures that may follow (in the case of repetions), the integers are separated by `, ` (comma + space).
