# Run graph_non_graph_heuristic_muscima_val_v1

- Baseline: deterministic non-graph geometry rules
- Input parity: same MUSCIMA split and same candidate edges as the GNN graph evaluation
- Primary metric: `positive_macro_f1`
- Primary value: `0.621796846824738`
- Edge count: `48174`
- Positive edge count: `6340`

## Positive Class Metrics

| relationship | precision | recall | f1 | support |
|---|---:|---:|---:|---:|
| stem_notehead | 0.29687813356507786 | 1.0 | 0.45783505154639176 | 4441 |
| beam_notegroup | 0.6473396998635743 | 0.9994734070563455 | 0.7857586421030842 | 1899 |
| slur_phrase | 0.0 | 0.0 | 0.0 | 0 |
| tie_sustained | 0.0 | 0.0 | 0.0 | 0 |

## Interpretation

This baseline does not perform message passing, attention, or learned edge classification.
It only checks local spatial proximity between noteheads, stems, and beams.
It is the required non-graph comparison for the graph-based project rubric.
