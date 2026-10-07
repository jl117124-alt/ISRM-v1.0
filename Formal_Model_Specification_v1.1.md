# ISRM v1.1 — canonical-model ambiguity correction

Status: proposed correction; canonical model unresolved. This is not a validated
new model release. The February 2026 v1.0 record remains byte-for-byte unchanged.
Use this specification with `isrm_v1_1_pipeline.py` and `ISRM v1.1.json`.

## Audit boundary and evidence

Audited 2026-10-07 at repository commit
`68d59ea45b6b4e3b2c8fb33e6623001a4296944d` (2026-02-18).
The checkout has one commit, one main branch, no tags, and eleven tracked files.
GitHub issues and pull requests were empty at audit time. All tracked text and
the complete two-page `Readme.pdf` were examined; no bundled dataset exists.

Immutable evidence links use this base:
https://github.com/jl117124-alt/ISRM-v1.0/tree/68d59ea45b6b4e3b2c8fb33e6623001a4296944d

| Evidence | Finding |
| --- | --- |
| `Formal_Model_Specification.md`, lines 15–18 | SP = S × TL × N × (1 + P) / (IRD × M). |
| Same file, lines 24–41 | S, IRD, M have descriptions; TL and N have none. P is a fragmentation amplifier described only as an optional scaling term. No proxy, units, bounds, normalization, or missing-value rule for TL/N/P is supplied. |
| `readme.md`, core equation | Repeats expanded equation; does not define TL/N or operationalize P. Claims correspondence to PDF pages 6–7. |
| `Readme.pdf`, pages 1–2 | Repeats README and expanded equation; contains no pages 6–7. No other PDF is tracked. The referenced original specification cannot be inspected from this repository. |
| `isrm_v1_pipeline.py`, docstring, REQUIRED_COLUMNS, add_sp_columns | Calls S / (IRD × M) canonical; computes that expression with no TL/N/P inputs. |
| `ISRM v1.0.txt`, lines 6–7 | Closes v1.0 and requires later modifications to increment the version. |
| Replication instructions, empirical statement, limits, falsifiers, ethics, license | Supply no missing TL/N/P definitions or explicit reduction decision. Validation claims cannot be independently reproduced without the panel and supporting results. |

Neither document precedence nor author intent is established by a single
simultaneous upload. The equations coincide when TL × N × (1 + P) = 1;
TL = N = 1 and P = 0 is one sufficient assignment, not a repository-supported
default. Silently adopting it would invent a modeling decision.

## Executable contract

v1.1 has **no canonical SP calculation** pending the decision below.
The wrapper requires explicit selection of `v1.0-minimal`; omission is an error.
That option reproduces the archived calculation under the identifier
`legacy-minimal`, not the expanded formal model. Expanded inputs TL/N/P are
rejected rather than silently ignored. No defaults for them are introduced.

The legacy calculation retains the archived definitions: S is the mean of
min-max-normalized log population, density, urban percentage and metro >1M
percentage; IRD averages normalized volunteerism, two-parent children and
turnout; M is normalized marriage rate. Zero denominator or nonfinite SP becomes
NaN. Enforcement remains validation-only. Existing missing-value, normalization,
quintile and plotting behavior is delegated unchanged, including known limits;
this correction does not certify those behaviors or the historical validation.

Run from the repository root:

```sh
python isrm_v1_1_pipeline.py --model v1.0-minimal
```

Uses `raw_data/combined_panel.csv` and the archived required columns. Writes the
same output filenames beneath `output/v1.1/` and `figures/v1.1/`, preserving v1.0
outputs. The panel adds `implementation_version`, `model_id`, and
`canonical_model_status` so the result cannot be mistaken for a resolved model.
The command identifies the unresolved status before running.

## Exact decision required

The model author must choose which expression is canonical for v1.1:

1. **Expanded:** SP = S × TL × N × (1 + P) / (IRD × M). Define TL and N's meanings,
   measurable proxies, units, admissible bounds, normalization domain/anchors,
   and missing/zero handling. Specify P's proxy and normalization and whether
   omission means zero. Identify the original specification and validation
   evidence, and reconcile M's marriage-only implementation versus the formal
   marriage/inverse-divorce description before claiming equivalence.
2. **Minimal:** SP = S / (IRD × M). Explicitly approve removal of TL/N/P or state
   the conditions under which the minimal form is the intended reduction.
   Identify which validation results apply to this form.

Until then neither expression is promoted to canonical. This v1.1 correction
records the conflict and offers labeled legacy reproduction only. Any subsequent
modification after a closed release must receive another version increment.
