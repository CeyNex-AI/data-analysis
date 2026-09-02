"""Shared helpers for the CeyNex data-source notebooks.

Every notebook in this folder reads straight from the `ceynex-core` checkout.
Nothing here copies or caches data, so re-running the ingest pipeline and
re-running a notebook shows fresh results.

Two things this module exists to get right, because getting them wrong is how
a notebook quietly analyses the wrong file:

1. **Where a connector actually looks for its data.** The agriculture
   connectors resolve their raw directory through a three-candidate search in
   `ceynex/data/pipeline.py::_agriculture_raw_dir`, not a fixed path. The
   apparel connectors use a fixed `data/raw/<source>/manual/` instead. Both are
   mirrored here rather than guessed.

2. **Dated snapshots.** Raw sources are saved under `<source>/YYYY-MM-DD/`, and
   the connectors read the *latest* such directory. `resolve()` mirrors
   `ceynex/data/connectors/_snapshots.py` so a notebook reads the same file the
   pipeline would.

These helpers are deliberately plain pandas. They do not import `ceynex`, so
they run on the `requirements.txt` environment (see the README note about the
Python version needed to import the connectors themselves).
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pandas as pd

# Anchored on this file, not the working directory, so a notebook run from
# anywhere still finds the checkout.
WORKSPACE = Path(__file__).resolve().parents[2]
CORE = WORKSPACE / "ceynex-core"
PARQUET = CORE / "data" / "parquet"
REF = CORE / "ceynex" / "data" / "reference"
CONFIG = CORE / "config"

_SNAPSHOT_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def agriculture_raw_dir() -> Path | None:
    """The directory M1's agriculture connectors read from, or None.

    Mirrors `pipeline._agriculture_raw_dir`: an explicit environment override
    first, then a sibling `data/raw` next to the repo, then the repo's own
    `data/raw`. The pipeline raises when none exist; a notebook would rather
    say so and carry on, so this returns None instead.
    """
    override = os.environ.get("CEYNEX_AGRICULTURE_RAW_DIR")
    candidates = [
        Path(override) if override else None,
        WORKSPACE / "data" / "raw",
        CORE / "data" / "raw",
    ]
    for candidate in candidates:
        if candidate is not None and candidate.is_dir():
            return candidate
    return None


def latest_snapshot(directory: Path) -> Path:
    """Return the newest `YYYY-MM-DD` child, or the directory itself."""
    directory = Path(directory)
    if not directory.is_dir():
        return directory
    snapshots = sorted(
        entry
        for entry in directory.iterdir()
        if entry.is_dir() and _SNAPSHOT_NAME.fullmatch(entry.name)
    )
    return snapshots[-1] if snapshots else directory


def resolve(directory: Path | None, filename: str | None = None) -> Path | None:
    """Resolve the file a connector would read, or None if it is not staged.

    `directory` may be the file itself (the connectors accept that too), a
    source directory containing dated snapshots, or None.
    """
    if directory is None:
        return None
    directory = Path(directory)
    if directory.is_file():
        return directory
    if filename is None:
        return directory if directory.is_dir() else None
    candidate = latest_snapshot(directory) / filename
    return candidate if candidate.exists() else None


def status(source: str, path: Path | None, filename: str | None = None, *, how: str = "") -> Path | None:
    """Print whether a source is staged locally, and return the file if it is.

    Prints the exact path the connector would read so a reader can stage the
    file without going back to the code to find out where it belongs.
    """
    resolved = resolve(path, filename)
    print(f"{source}")
    if resolved is not None:
        size = resolved.stat().st_size
        print(f"  staged: {resolved}")
        print(f"  size:   {size:,} bytes")
        return resolved

    expected = Path(path) / (filename or "") if path is not None else None
    print("  staged: NO — the analysis cells below will skip.")
    if expected is not None:
        print(f"  expected at: {expected}")
    else:
        print("  expected at: no raw directory found on this machine")
    if how:
        print(f"  how to get it: {how}")
    return None


def reference(name: str, **read_csv_kwargs) -> pd.DataFrame:
    """Read one of the committed reference CSVs, skipping `#` comment lines."""
    read_csv_kwargs.setdefault("comment", "#")
    return pd.read_csv(REF / name, **read_csv_kwargs)


def comtrade_parquet() -> pd.DataFrame:
    """Load the ingested Comtrade facts, restoring the hive partition columns.

    Reading the individual parquet files directly loses `sector`, `item` and
    `year`, which live in the directory names rather than the files. Reading
    the partition root keeps them.
    """
    if not PARQUET.is_dir():
        raise FileNotFoundError(f"no parquet output at {PARQUET}; run `make ingest` first")
    frame = pd.read_parquet(PARQUET)
    for column in ("sector", "item", "year"):
        if column in frame.columns:
            frame[column] = frame[column].astype(str)
    if "year" in frame.columns:
        frame["year"] = pd.to_numeric(frame["year"], errors="coerce").astype("Int64")
    return frame


def fact_trade_columns() -> list[str]:
    """The frozen `fact_trade` measure columns every connector maps onto."""
    return [
        "source_id",
        "sector",
        "item",
        "hs_code",
        "reporter_iso3",
        "reporter_m49",
        "partner_iso3",
        "partner_m49",
        "period_start",
        "period_end",
        "frequency",
        "export_volume",
        "volume_unit",
        "export_value_usd",
        "price",
        "price_unit",
        "fx_usd_lkr",
        "source_hash",
    ]
