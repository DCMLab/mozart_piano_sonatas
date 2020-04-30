## Columns

The TSVs in this folder each contain all cadence labels of one of the movements with their temporal positions. The column `presence` shows with which parameters of `mozart_loader.py` the column is present, where `raw` means that the column is present in the raw data and will be output with `-C`.

Cadence labels mark the end of the cadence. In most cases this is the final chord but in cases with suspensions over the final chord, the label marks the point of resolution.

| column | type | presence | description |
|-----------------|----------|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **mn** | integer | raw | Measure number, continuous count of complete measures as used in printed editions. Starts with 1 except for pieces beginning with a pickup measure, numbered as 0. |
| **playthrough** | integer | u | For the unfolded representations, a running count of complete measures disambiguating repeated MNs. |
| **timesig** | string | e/E/g/a/A | Time signature of the measure in which the cadence ends. |
| **beat** | fraction | e/E/g/a/A | On which beat the cadence ends, expressed as string. Downbeat positions are just integers (e.g. `'1'`) and upbeat positions have a fraction of the respective beat size attached, for instance, in `2/2` meter, beat `'1.1/2'` is on the second quarter note and beat `'1.1/3'` is on the second quarter triplet note.<br> The mapping timesig => beat size is `'2/2' => 1/2, '4/4' => 1/4, '2/4' => 1/4, '3/8' => 1/8, '6/8' => 3/8`} |
| **onset** | fraction | raw | Label's temporal position from beat 1 of the measure, expressed in fractions of a whole note (1/4 = quarter note, 1/12 = triplet eigth, etc.) |
| **cadence** | string | raw | Cadence label. Can be  `PAC` (Perfect Authentic Cadence), `IAC` (Imperfect Authentic Cadence), `HC` (Half Cadence), `DC` (Deceptive Cadence), or `EC` (Evaded Cadence). |
