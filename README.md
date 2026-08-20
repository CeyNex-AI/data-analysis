# CeyNex data analysis

Exploratory Jupyter notebooks for the six data sources named in CeyNex's
design (`ceynex-core/docs/DATA_SOURCES.md`). Notebooks read directly from
`../ceynex-core/data/...` via relative paths — nothing here is a copy of the
data, so re-running the ingest pipeline and re-running a notebook shows
fresh results.

| # | Source | Status | Notebook |
|---|---|---|---|
| 1 | UN Comtrade | Built, real data (4,625 rows, 2015-2024) | `01_un_comtrade.ipynb` |
| 2 | FAOSTAT | Connector exists, no data staged yet (owner: M1) | `02_faostat.ipynb` |
| 3 | Central Bank of Sri Lanka | No connector yet (owner: M1) | `03_central_bank_sri_lanka.ipynb` |
| 4 | JAAF | Connector exists, no data staged yet (owner: M3) | `04_jaaf.ipynb` |
| 5 | EDB | Connector exists, no data staged yet (owner: M3) | `05_edb.ipynb` |
| 6 | WITS | Deliberately cut/deferred, no connector (see `DEFERRED.md`) | `06_wits.ipynb` |

Only UN Comtrade has data on disk today, so `01_un_comtrade.ipynb` is a full
analysis (cleaning, sanity checks against the documented figures, trend and
partner-country breakdowns). The other five are runnable scaffolds — they
detect that no data exists yet, document the expected schema (from each
source's `PROFILE.md` where one exists), and leave TODO sections ready to
fill in once real data lands.

## Running

```bash
pip install -r requirements.txt
jupyter notebook notebooks/
```
