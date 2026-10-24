from datetime import datetime
from pathlib import Path
import shutil
import sqlite3
import pandas as pd
import db

REQUIRED = {"caller_id", "call_timestamp", "time_duration_seconds", "call_type"}


def move_file(path, folder):
    target = Path(folder) / path.name
    if target.exists():
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = Path(folder) / f"{stamp}_{path.name}"
    shutil.move(str(path), str(target))


def ingest_folder(folder="incoming"):
    done = 0
    failed = 0
    for path in sorted(Path(folder).glob("*.csv")):
        try:
            calls_df = pd.read_csv(path)
            missing = REQUIRED - set(calls_df.columns)
            if missing:
                raise ValueError(f"missing columns {sorted(missing)}")
            db.import_calls(path.name, calls_df)
        except (pd.errors.EmptyDataError, pd.errors.ParserError, ValueError, sqlite3.IntegrityError) as e:
            print(f"FAILED {path.name}: {e}")
            move_file(path, "failed")
            failed += 1
        except sqlite3.OperationalError as e:
            print(f"RETRY LATER {path.name}: {e}")
        else:
            print(f"IMPORTED {path.name}")
            move_file(path, "processed")
            done += 1
    return done, failed