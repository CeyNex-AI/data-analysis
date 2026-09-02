# CeyNex data analysis

One notebook per data source. Each reads directly from the `ceynex-core`
checkout via `_common.py` — nothing here copies data, so re-running the ingest
pipeline and re-running a notebook shows fresh results.

## The sources

| # | Source | Connector | Data staged here? | Notebook |
|---|---|---|---|---|
| 1 | UN Comtrade | ✅ `comtrade.py` | ✅ **4,625 rows, 2015–2024** | `01_un_comtrade.ipynb` |
| 2 | FAOSTAT | ✅ `faostat.py` | ❌ | `02_faostat.ipynb` |
| 3 | Central Bank of Sri Lanka | ❌ none — planned | ❌ | `03_central_bank_sri_lanka.ipynb` |
| 4 | JAAF | ✅ `jaaf.py` | ❌ | `04_jaaf.ipynb` |
| 5 | EDB | ✅ `edb.py` | ❌ | `05_edb.ipynb` |
| 6 | WITS | ❌ **cut on purpose** | ❌ | `06_wits.ipynb` |
| 7 | Sri Lanka Tea Board | ✅ `teaboard.py` | ❌ | `07_tea_board.ipynb` |
| 8 | World Bank Pink Sheet | ✅ `pinksheet.py` | ❌ | `08_pink_sheet.ipynb` |
| 9 | Cinnamon fallback | ✅ `cinnamon.py` | ❌ | `09_cinnamon.ipynb` |

**Only UN Comtrade has data in this checkout.** The other eight notebooks run
end to end anyway: each one probes the exact path its connector would read,
prints where the file belongs if it is not there, and skips its analysis cells
cleanly instead of erroring.

Several sections work with no staged data at all, because they read committed
reference files rather than raw downloads:

- **`05_edb.ipynb` §5** reproduces the `APPAREL`/`APPREL` bug and its fix live
  from `item_vocabulary.csv`. This is the best single demo in the folder.
- **`03_central_bank_sri_lanka.ipynb` §1** shows the missing FX connector as a
  100%-empty `fx_usd_lkr` column rather than just asserting the gap.
- **`06_wits.ipynb`** prints the elasticity constants and agreement tables that
  stand in for the cut tariff source.
- **`09_cinnamon.ipynb` §8** cross-checks against ingested Comtrade cinnamon.

## Where each source's files belong

Two different conventions, and they are easy to mix up:

**Agriculture** (FAOSTAT, Tea Board, Pink Sheet, Cinnamon) resolves its raw
directory through the same three-candidate search as
`pipeline._agriculture_raw_dir` — first `$CEYNEX_AGRICULTURE_RAW_DIR`, then
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
import from `ceynex` directly. **That needs Python 3.12.** The connectors use
`datetime.UTC`, which does not exist before 3.11, so on an older interpreter the
import fails with a confusing `ImportError: cannot import name 'UTC'`.

Every such import is wrapped in a `try/except` that says so rather than dying,
and no notebook *requires* it — the analysis paths use plain pandas. But if a
connector cell reports it could not import, this is why.

The `ceynex.data.crosswalk` module is the exception: it has no 3.11+ imports and
works anywhere, which is why the EDB vocabulary demo runs on any interpreter.
