#!/usr/bin/env python3
"""
Fetch a Google Sheet tab and write it to temp_data.json.

Usage:
    python fetch.py <spreadsheet_id> <tab_name>
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = SCRIPT_DIR.parent / "temp_data.json"


def get_worksheet(spreadsheet_id: str, tab_name: str):
    import gspread

    credentials_path = SCRIPT_DIR.parent / "credentials" / "service-account.json"
    if not credentials_path.exists():
        print(f"ERROR: Credentials not found at {credentials_path}", file=sys.stderr)
        sys.exit(1)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
    ]

    try:
        gc = gspread.service_account(filename=str(credentials_path), scopes=scopes)
    except Exception as e:
        print(f"ERROR: Failed to authenticate with service account: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        spreadsheet = gc.open_by_key(spreadsheet_id)
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"ERROR: Spreadsheet '{spreadsheet_id}' not found or not accessible.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to open spreadsheet: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        return spreadsheet.worksheet(tab_name)
    except gspread.exceptions.WorksheetNotFound:
        print(f"ERROR: Tab '{tab_name}' not found in spreadsheet.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to access tab: {e}", file=sys.stderr)
        sys.exit(1)


def parse_worksheet(worksheet) -> dict:
    all_values = worksheet.get_all_values()
    if not all_values:
        print("ERROR: Sheet is empty.", file=sys.stderr)
        sys.exit(1)
    headers = all_values[0]
    rows = all_values[1:]
    return {"headers": headers, "rows": rows}


def write_output(
    data: dict,
    spreadsheet_id: str,
    tab_name: str,
    output_path: Path = OUTPUT_PATH,
) -> None:
    output = {
        "spreadsheet_id": spreadsheet_id,
        "tab": tab_name,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "headers": data["headers"],
        "rows": data["rows"],
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"Fetched {len(data['rows'])} row(s) from tab '{tab_name}'.")
    print(f"Output written to: {output_path}")


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python fetch.py <spreadsheet_id> <tab_name>",
            file=sys.stderr,
        )
        sys.exit(1)

    spreadsheet_id = sys.argv[1]
    tab_name = sys.argv[2]

    worksheet = get_worksheet(spreadsheet_id, tab_name)
    data = parse_worksheet(worksheet)
    write_output(data, spreadsheet_id, tab_name)


if __name__ == "__main__":
    main()
