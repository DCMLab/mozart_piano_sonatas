# Harmony and Phrase Annotations

Within the major-minor system of the Classical period, the pitch collection for a key can be said to consist of a root pitch and a major or (natural) minor scale built on that pitch. Therefore, we express keys using a common shorthand where capitals denote the root of a major key and lowercase letters that of a minor key. At the beginning of each piece (or movement), the global key is indicated by the absolute note name of its root (see \ref{tab:features}). 
% implying that the local key is \Q{I} or \Q{i}. 
% The roots of the local keys are expressed in terms of Roman numerals relative to the root of the global key (including the key of the tonic, \Q{I} or \Q{i}). 

In the annotation syntax, changes of the local key (modulations) are prepended to the actual chord label where the change occurs, separated by a period. 


is based on triads with three chord tones (root, third, and fifth) and seventh chords with four chord tones. A chord's type is defined by the interval classes between the root (as the lowest voice) and the remaining chord tones.
In addition, chord inversion, defined by the chord tone which is put lowest, is expressed as the generic intervals that the other chord tones form with the bass note (conventional figured bass notation). The XXX standard expresses a chordal root as a Roman numeral that determines its position with respect to the scale of the current local key (or of a lower-level key), preceded by accidentals where needed to indicate modifications of the default scale. 
\autoref{tab:chords} shows how the case of the Roman numeral (represented as RN for uppercase and rn for lowercase) in combination with the features \textit{Type} and \textit{Inversion} defines the chord tones. Note that the \textit{Root} defines merely the root's position in the scale and the size of the third above, while \textit{Inversion} distinguishes triads from tetrads; all three features are needed, however, in order to define the complete \textit{Chord type}.
\begin{table}[htb]
\centering
\resizebox{\columnwidth}{!}{%
\begin{tabular}{@{}llll@{}}
\toprule
Root & Type & Inversions   & Chord type              \\ \midrule
RN   & <NA> & <NA>, 6, 64  & Major triad             \\
rn   & <NA> & <NA>, 6, 64  & Minor triad             \\
rn   & o    & <NA>, 6, 64  & Diminished triad        \\
RN   & +    & <NA>, 6, 64  & Augmented triad         \\
RN   & <NA> & 7, 65, 43, 2 & Dominant seventh        \\
rn   & <NA> & 7, 65, 43, 2 & Minor seventh           \\
rn   & o    & 7, 65, 43, 2 & Diminished seventh      \\
rn   & \%   & 7, 65, 43, 2 & Half-diminished seventh \\
RN   & M    & 7, 65, 43, 2 & Major seventh           \\
rn   & M    & 7, 65, 43, 2 & Minor major seventh     \\
RN   & +    & 7, 65, 43, 2 & Augmented minor seventh \\
RN   & +M    & 7, 65, 43, 2 & Augmented major seventh \\\bottomrule
\end{tabular}%
}
\caption{Possible feature combinations for defining chord tones. The first column represents the case of the chord root's Roman numeral. <NA> stands for absence of the feature.}
\label{tab:chords}
\end{table}

The annotation standard contains three special symbols for the augmented sixth chords which cannot confidently be expressed in terms of a root, namely \Q{It6} for the Italian, \Q{Ger} for the German, and \Q{Fr} for the French sixth chord. 

## Columns

The TSVs in this folder each contain all chord labels of one of the movements with their temporal positions. The column `presence` shows with which parameters of `mozart_loader.py` the column is present, where `raw` means that the column is present in the raw data and will be output with `-H`. The raw data contain only the columns `mc, mn, onset, label`. The derived feature columns are available via `mozart_loader.py [-e]` or, with chord tones added for each label, via one of the parameters `mozart_loader.py [-E][-g][-a][-A]`.

For all features given as Roman numerals (`localkey, pedal, numeral, relativeroot`), the scale degrees `III, VI, VII` depend on the local mode: In a local minor key (`localkey_is_minor == 1`), they are a minor 3rd/6th/7th above the local tonic, in major, a major 3rd/6th/7th.

The data type `Int64` stands for integer columns containing NULL values.

| column | type | presence | description |
|--------------------|------------|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **mc** | integer | raw | Measure count, identifier for the measure units in the XML encoding. Always starts with 1 for correspondence to MuseScore's status bar. |
| **mn** | integer | raw | Measure number, continuous count of complete measures as used in printed editions. Starts with 1 except for pieces beginning with a pickup measure, numbered as 0. |
| **playthrough** | integer | u | For the unfolded representations, a running count of complete measures disambiguating repeated MNs. |
| **timesig** | string | e/E/g/a/A | Time signature of the measure in which the label occurs. |
| **beat** | fraction | e/E/g/a/A | On which beat the label occurs, expressed as string. Downbeat positions are just integers (e.g. `'1'`) and upbeat positions have a fraction of the respective beat size attached, for instance, in `2/2` meter, beat `'1.1/2'` is on the second quarter note and beat `'1.1/3'` is on the second quarter triplet note.<br> The mapping timesig => beat size is `'2/2' => 1/2, '4/4' => 1/4, '2/4' => 1/4, '3/8' => 1/8, '6/8' => 3/8`} |
| **onset** | fraction | raw | Label's temporal position from beat 1 of the measure, expressed in fractions of a whole note (1/4 = quarter note, 1/12 = triplet eigth, etc.) |
| **label** | string | raw | Original chord label as entered by the annotator. |
| **volta**   | Int64  | raw **only**   | Disambiguates endings: `1` for first endings, `2` for second endings. This column is present only for disambiguation in the raw data because `mozart_loader.py` has been designed to correctly deal with first and second endings by deleting first endings or unfolding repetitions (parameter `-u`).  |
| **alt_label** | string | e/E/g/a/A | Alternative annotation as added by the annotator. |
| **globalkey** | string | e/E/g/a/A | Tonality of the piece, expressed as absolute note name, e.g. 'Ab' for A flat major, or `g#` for G sharp minor. |
| **localkey** | string | e/E/g/a/A | Local key expressed as Roman numeral relative to the `globalkey`, e.g. `IV` for the major key on the 4th scale degree or `#iv` for the minor scale on the raised 4th scale degree. |
| **pedal** | string | e/E/g/a/A | If the chord occurs over a pedal note, this pedal note is expressed as a Roman numeral. If the chord tones are being computed (see below), this additional note is not taken into account and would need to be added as bass note. |
| **chord** | string | e/E/g/a/A | This is simply a compact view of the features that define the chord tones, namely `numeral, form, figbass, changes, relativeroot`. |
| **numeral** | string | e/E/g/a/A | Roman numeral defining the chordal root relative to the local key. An uppercase numeral stands for a major chordal third, lowercase for a minor third. If chord tones are being computed, the column `root` expresses the same information as an absolute interval. |
| **special** | string | e/E/g/a/A | Labels containing special chord names are being replaced and the special names go in this column. Special names can be `Ger, Fr, It` for the three 'geographical chords', i.e. for the augmented sixth chords. |
| **form** | string | e/E/g/a/A | `<NA>`: The chord is either a major or minor triad if `figbass` is one of `<NA>, '6', '64'`. Otherwise, it is either a major or a minor chord with a minor seventh.<br>`o, +`: Diminished or augmented chord. Again, it depend on `figbass` whether it is a triad or a seventh chord.<br>`%, M`: Half diminished or major seventh chord. For the latter, the chord form depends on the Roman numeral. |
| **figbass** | string | e/E/g/a/A | Figured bass notation of the chord inversion. For triads, this feature can be `<NA>, '6', '64'`, for seventh chords `'7', '65', '43', '2'`. This features is decisive for which chord tone is in the bass. |
| **changes** | string | e/E/g/a/A | A string containing all **added** intervals, all **replacing** intervals, and all chord tone **alterations**. All intervals are given as arabic numbers standing for the scale degree found above the `numeral` in the current local scale. E.g., `+6`, over the numeral `V`, would add a major sixth in a local major key, and a minor sixth in a local minor key. A minor sixth added to the dominant in a major key would be `+b6`. **Replacing** intervals and **alterations** are not preceded by `+`. Alterations are changes to the chord tones `3, 5, 8, 10, 12`. All other intervals replace a chord tone. If preceded by `#`, they replace the upper neighbor (e.g. `#2` replace the chordal third. Otherwise, they replace the lower neighbour (e.g. `2` replaces the root, `9` replaces the octave). |
| **relativeroot** | string | e/E/a/A | This feature designates a lower-level key to which the current chord relates. It is expressed relative to the local key. For example, if the current numeral is a `V` and it is a secondary dominant, `relativeroot` is the scale degree that is being tonicized. Column is not present if the chord labels are relative to the global key.|
| **phraseend** | string | e/E/g/a/A | If the chord ends a phrase, this feature is `\\`. |
| **chord_type** | string | e/E/g/a/A | A summary of information that otherwise depends on the three columns `numeral, form, figbass`. It can be one of the wide-spread abbreviations for triads: `M, m, o, +` or for seventh chords: `o7, %7, +7` (for diminished, half-diminished and augmented seventh chords), or `Mm7, mm7, MM7, mM7`for all combinations of a major/minor triad with a minor/major seventh. |
| globalkey_is_minor | boolean | e/E/g/a/A | For convenience. `1`: global key is a minor key, `0`: global key is a major key. |
| localkey_is_minor | boolean | e/E/a/A | For convenience. `1`: local key is a minor key, `0`: local key is a major key. Column is not present if the chord labels are relative to the global key.|
| chord_tones | collection | E/a/A | Exactly three tones for triads and four tones for seventh chords. They appear in ascending order, starting from the bass note ('closed form'). Replaced or altered chord tones are taken into account. Tones are expressed as stack-of-fifths intervals where 0 is the local tonic. With parameters `-g` or `-A`, however, 0 is the global tonic. With parameter `-a`, 0 is equal to the absolute pitch of the global key. |
| added_tones | collection | E/a/A | Contains any number of added chord tones. |
| root | integer | E/a/A | Chordal root expressed as stack-of-fifths interval. |
| bass_note | integer | E/a/A | Always the first integer in `chord_tones`. |
