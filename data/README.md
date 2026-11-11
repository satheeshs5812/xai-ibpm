# Data

The four event logs are public 4TU.ResearchData releases. They are **not** included in this repository.
Download each log from its DOI, and place the gzipped XES file in `data/raw/` under the file name given below
(rename the downloaded file if necessary).

| Log | Reference | DOI | Expected file in `data/raw/` |
|---|---|---|---|
| BPIC2012 | van Dongen, B. F. (2012). *BPI Challenge 2012* [Data set]. 4TU.ResearchData. | https://doi.org/10.4121/uuid:3926db30-f712-4394-aebc-75976070e91f | `BPI_Challenge_2012.xes.gz` |
| BPIC2017 | van Dongen, B. F. (2017). *BPI Challenge 2017* [Data set]. 4TU.ResearchData. | https://doi.org/10.4121/uuid:5f3067df-f10b-45da-b98b-86ae4c7a310b | `BPI_Challenge_2017.xes.gz` |
| Sepsis | Mannhardt, F. (2016). *Sepsis cases – event log* [Data set]. 4TU.ResearchData. | https://doi.org/10.4121/uuid:915d2bfb-7e84-49ad-a286-dc35f063a460 | `Sepsis_Cases.xes.gz` |
| Traffic Fines | de Leoni, M., & Mannhardt, F. (2015). *Road traffic fine management process* [Data set]. 4TU.ResearchData. | https://doi.org/10.4121/uuid:270fd440-1057-4fb9-89a9-b699b47990f5 | `Road_Traffic_Fine_Management_Process.xes.gz` |

If a release is distributed as an uncompressed `.xes` file, compress it with `gzip` first (the checksums below refer
to the `.xes.gz` files used in the paper; a re-compressed file can have a different checksum even when the log is
identical, in which case compare the event and case counts below instead).

## Expected layout

```
data/
├── raw/                                   # you create this (git-ignored)
│   ├── BPI_Challenge_2012.xes.gz
│   ├── BPI_Challenge_2017.xes.gz
│   ├── Sepsis_Cases.xes.gz
│   └── Road_Traffic_Fine_Management_Process.xes.gz
├── parsed/                                # written by scripts/01_parse_logs.sh (git-ignored)
│   └── bpic2012.parquet, bpic2017.parquet, sepsis.parquet, traffic.parquet
└── SHA256SUMS
```

## Verification

`scripts/01_parse_logs.sh` checks the files against `data/SHA256SUMS` before parsing. Manually:

```bash
cd data/raw && sha256sum -c ../SHA256SUMS
```

| File | SHA-256 | Events | Cases |
|---|---|---|---|
| `BPI_Challenge_2012.xes.gz` | `5cd9cc16b9bcb20bd4aae45666a5d87479ddbf47e6371618b6ad217174cecdf3` | 262,200 | 13,087 |
| `BPI_Challenge_2017.xes.gz` | `183c5e5189282779c811c78c33ff936351b3dd201165d612211fc220936f8249` | 1,202,267 | 31,509 |
| `Sepsis_Cases.xes.gz` | `709c52340306415952811b9b9c5dc6bcc8f8d47d583eba39df9a538459dc543a` | 15,214 | 1,050 |
| `Road_Traffic_Fine_Management_Process.xes.gz` | `dc9e0e65c964c8ce2a720687ecf17d8204a5cced5db2267c717ed39ada665da8` | 561,470 | 150,370 |

Event and case counts are those of the parsed tables (`data/parsed/*.parquet`) before labelling.

## Preprocessing reference

The BENCHMARK protocol re-implements the labelling and preprocessing of the public benchmark of
Teinemaa et al. (2019), *Outcome-oriented predictive process monitoring: review and benchmark*, ACM TKDD
(code: https://github.com/irhete/predictive-monitoring-benchmark, `preprocessing/` and `experiments/dataset_confs.py`).
That code is not needed to run this repository; `src/prepare.py` contains the re-implementation, and
`src/common.py` (`COLS`, `TASKS`) lists the feature columns and label definitions taken from it.
