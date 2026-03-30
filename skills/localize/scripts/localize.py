#!/usr/bin/env python3
"""
Append pre-translated rows to Google Sheet.

Usage:
    python localize.py <json_file>

    json_file: JSON file containing an array of rows.
    Each row is an array of strings in column order:
    [Key, English, German, Korean, Japanese, French, Spanish, Portuguese, Russian, Italian, Chinese (Simplified), Chinese (Traditional)]
"""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
COMMAND_DIR = SCRIPT_DIR.parent
CONFIG_DIR = COMMAND_DIR / "config"


def load_sheet_config():
    with open(CONFIG_DIR / "sheet-config.json", encoding="utf-8") as f:
        return json.load(f)


def append_to_sheet(rows, sheet_config):
    """Append rows to the Google Sheet. Never removes existing data."""
    import gspread
    from google.oauth2 import service_account

    credentials_path = str(COMMAND_DIR / "credentials" / "service-account.json")

    if not Path(credentials_path).exists():
        print(f"ERROR: Credentials not found at {credentials_path}", file=sys.stderr)
        sys.exit(1)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = service_account.Credentials.from_service_account_file(credentials_path, scopes=scopes)
    gc = gspread.authorize(creds)

    sheet = gc.open_by_key(sheet_config["sheet_id"])
    worksheet = sheet.worksheet(sheet_config["tab_name"])

    worksheet.append_rows(rows, value_input_option="USER_ENTERED")
    return len(rows)


def main():
    if len(sys.argv) != 2:
        print("Usage: python localize.py <json_file>", file=sys.stderr)
        sys.exit(1)

    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f"ERROR: File not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    with open(json_path, encoding="utf-8") as f:
        rows = json.load(f)

    if not rows:
        print("ERROR: No rows to append.", file=sys.stderr)
        sys.exit(1)

    sheet_config = load_sheet_config()

    if sheet_config["sheet_id"] == "YOUR_GOOGLE_SHEET_ID_HERE":
        print("ERROR: Sheet ID not configured.", file=sys.stderr)
        sys.exit(1)

    count = append_to_sheet(rows, sheet_config)
    print(f"Appended {count} row(s) to sheet.")


if __name__ == "__main__":
    main()
