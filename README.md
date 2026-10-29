# Voicebot Call Log Analyzer

A small app that stores voicebot call logs, imports batches of CSV files (by hand or on a timer), labels each call with an outcome using simple rules, and shows call-volume and failure-rate statistics.

## Features

- **Add, edit and delete calls** in a Streamlit page, with checks on the caller number, timestamp and call type.
- **Import a CSV file** from the page. The file is checked for the required columns and valid caller numbers first.
- **Scheduled ingestion:** CSV files dropped into the `incoming/` folder are imported automatically every 30 seconds. Imported files move to `processed/`, rejected ones to `failed/`. A file still being copied is skipped until it has been quiet for 5 seconds.
- **All-or-nothing imports:** if any row in a file is invalid, nothing from that file is saved. Each file name can be imported only once.
- **Outcome tagging:** every call gets an outcome from its duration. Editing a call clears its outcome and re-tags it.
- **Statistics:** total calls, dropped and escalated counts, failure rate, and charts per outcome, per day and per call type.

## Outcome rules

| Outcome | Rule |
|---|---|
| `dropped` | Duration of 10 seconds or less |
| `escalated` | Duration above 200 seconds |
| `resolved` | Everything in between |

Failure rate = (dropped + escalated) / tagged calls. The thresholds are two constants at the top of `tagging.py`.

## CSV format

The first line must contain these column names:

```
caller_id,call_timestamp,time_duration_seconds,call_type
+91-9800000011,2026-10-03 09:00:00,95,inbound
```

- `caller_id`: a 10-digit mobile number starting with 6-9, with or without `+91` (for example `9800000011` or `+91-9800000011`).
- `call_timestamp`: `YYYY-MM-DD HH:MM:SS`.
- `time_duration_seconds`: whole seconds.
- `call_type`: `inbound` or `outbound` (lowercase).

## Setup (Windows PowerShell)

```powershell
pip install -r requirements.txt
mkdir incoming, processed, failed
python init_db.py
```

`init_db.py` creates `calls.db` with two tables: `ingest_batches` (one row per imported file) and `calls` (one row per call).

## Run

Open two terminals in the project folder:

```powershell
python -m streamlit run app.py      # the web page, at http://localhost:8501
python run_scheduler.py             # the folder watcher; press Ctrl+C to stop
```

To try the scheduler, copy a CSV from `sample_calls_*.csv` into `incoming/`.

## Project layout

| File | Purpose |
|---|---|
| `app.py` | Streamlit page: forms, import, tables and statistics |
| `db.py` | Database functions: add, update, delete, get, import |
| `init_db.py` | Creates the database and tables |
| `ingest.py` | Imports every CSV in `incoming/` and moves it to `processed/` or `failed/` |
| `run_scheduler.py` | Runs ingestion and tagging every 30 seconds |
| `tagging.py` | Outcome rules and the tagger |
| `stats.py` | Queries behind the statistics section |
| `validation.py` | Caller-number check |
| `sample_calls_*.csv` | Example files for trying the import |

## Known limits

- The scheduler runs only while its terminal window is open.
- The same caller can be stored in different spellings (`9800000011` and `+91-9800000011`), so counts per caller would treat them as separate.
- Duplicate calls are not detected.
- The `incoming/`, `processed/` and `failed/` folders and `calls.db` are not stored in Git.