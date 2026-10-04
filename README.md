# CeyNex data analysis

Exploratory analysis of every data source behind **CeyNex**, a multi-agent decision intelligence platform for Sri Lanka's export economy. There is one Jupyter notebook per source. Each notebook profiles the raw files, checks coverage and units, and shows the problems the ingest pipeline in [`ceynex-core`](https://github.com/CeyNex-AI/ceynex-core) had to solve.

Group 07, Project P16, CS3501 Data Science and Engineering Project, University of Moratuwa.

The notebooks read directly from a `ceynex-core` checkout through `notebooks/_common.py`. Nothing in this repo copies data, so re-running the ingest pipeline and then re-running a notebook shows fresh results.

## The sources

| # | Source | Connector in ceynex-core | In production | Notebook |
|---|---|---|---|---|
| 1 | UN Comtrade | `comtrade.py` | Yes, monthly refresh | `01_un_comtrade.ipynb` |
| 2 | FAOSTAT | `faostat.py` | Yes | `02_faostat.ipynb` |
| 3 | Central Bank of Sri Lanka (FX) | replaced by `fx.py` (World Bank LKR/USD, `WB_FX`) | Yes, as `WB_FX` | `03_central_bank_sri_lanka.ipynb` |
| 4 | JAAF | `jaaf.py` | Yes | `04_jaaf.ipynb` |
| 5 | EDB | `edb.py` | Yes | `05_edb.ipynb` |
| 6 | WITS | none, cut on purpose | No | `06_wits.ipynb` |
| 7 | Sri Lanka Tea Board | `teaboard.py` (curated workbook) | Yes, with row-level provenance | `07_tea_board.ipynb` |
| 8 | World Bank Pink Sheet | `pinksheet.py` | Yes, monthly refresh | `08_pink_sheet.ipynb` |
| 9 | Cinnamon | `cinnamon.py` (curated workbook) | Yes, with row-level provenance | `09_cinnamon.ipynb` |

Production holds 13,132 trade observations from 8 sources (October 2026). The notebooks were written in August and September 2026, when much of this data had not yet been ingested. A notebook whose raw files are missing from your checkout still runs end to end. It probes the exact path its connector would read, prints where the file belongs, and skips its analysis cells instead of failing.

Several sections need no staged data at all, because they read committed reference files:

- **`05_edb.ipynb` section 5** reproduces the `APPAREL`/`APPREL` vocabulary bug and its fix from `item_vocabulary.csv`.
- **`03_central_bank_sri_lanka.ipynb` section 1** shows why an FX source was needed, using the empty `fx_usd_lkr` column from before `WB_FX` was added.
- **`06_wits.ipynb`** prints the elasticity constants and agreement tables that stand in for the cut tariff source.
- **`09_cinnamon.ipynb` section 8** cross-checks the cinnamon figures against the ingested Comtrade data.

## Where each source's files belong

Two different conventions, and they are easy to mix up:

**Agriculture** (FAOSTAT, Tea Board, Pink Sheet, Cinnamon) resolves its raw
directory through the same three-candidate search as
`pipeline._agriculture_raw_dir` - first `$CEYNEX_AGRICULTURE_RAW_DIR`, then
`data/raw/` beside the repo, then `ceynex-core/data/raw/`. Inside that, the
newest `YYYY-MM-DD` snapshot directory wins.

**Apparel** (EDB, JAAF) uses a fixed `ceynex-core/data/raw/<source>/manual/`.
The paths are committed; the files are gitignored, so each teammate stages
their own copy.

Every notebook prints its own resolved path, so run the first code cell rather
than working this out by hand.

## Running

```bash
pip install -r requirements.txt
jupyter notebook notebooks/
```

`_common.py` anchors its paths on its own file location, so notebooks work from
any working directory.

### A version trap worth knowing

Two of these notebooks (`05_edb.ipynb`, and any cell importing a connector)
import from `ceynex` directly. **That needs Python 3.11 or later.** The connectors use
`datetime.UTC`, which does not exist before 3.11, so on an older interpreter the
import fails with a confusing `ImportError: cannot import name 'UTC'`.

Every such import is wrapped in a `try/except` that says so rather than dying,
and no notebook *requires* it - the analysis paths use plain pandas. But if a
connector cell reports it could not import, this is why.

The `ceynex.data.crosswalk` module is the exception: it has no 3.11+ imports and
works anywhere, which is why the EDB vocabulary demo runs on any interpreter.

## Team

Notebooks: Thisen Ekanayake (230170B). Team: Senindu Dinapura (230151T), Dhinanjaya Fernando (230181J). Supervisor: Dr. Chathuranga Hettiarachchi, University of Moratuwa.
