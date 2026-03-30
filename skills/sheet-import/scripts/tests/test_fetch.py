"""Tests for fetch.py — Google Sheets fetcher."""
import json
from unittest.mock import MagicMock, patch
import pytest

import fetch


class TestFetchSheet:
    def test_returns_headers_and_rows(self):
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_values.return_value = [
            ["itemId", "dropChance", "maxStack"],
            ["1_MB_Sub", "0.35", "5"],
            ["1_MB_Main", "0.15", "3"],
        ]
        result = fetch.parse_worksheet(mock_worksheet)
        assert result["headers"] == ["itemId", "dropChance", "maxStack"]
        assert result["rows"] == [
            ["1_MB_Sub", "0.35", "5"],
            ["1_MB_Main", "0.15", "3"],
        ]

    def test_empty_sheet_returns_empty_rows(self):
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_values.return_value = [["itemId", "dropChance"]]
        result = fetch.parse_worksheet(mock_worksheet)
        assert result["headers"] == ["itemId", "dropChance"]
        assert result["rows"] == []

    def test_completely_empty_sheet_raises(self):
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_values.return_value = []
        with pytest.raises(SystemExit) as exc_info:
            fetch.parse_worksheet(mock_worksheet)
        assert exc_info.value.code == 1


class TestGetWorksheet:
    def test_get_worksheet_missing_credentials_exits(self, tmp_path, monkeypatch):
        monkeypatch.setattr(fetch, "SCRIPT_DIR", tmp_path / "scripts")
        with pytest.raises(SystemExit) as exc_info:
            fetch.get_worksheet("fake_id", "Sheet1")
        assert exc_info.value.code == 1


class TestWriteOutput:
    def test_writes_json_with_required_fields(self, tmp_path):
        output_path = tmp_path / "temp_data.json"
        data = {
            "headers": ["itemId", "dropChance"],
            "rows": [["1_MB_Sub", "0.35"]],
        }
        fetch.write_output(
            data=data,
            spreadsheet_id="abc123",
            tab_name="DropRates",
            output_path=output_path,
        )
        result = json.loads(output_path.read_text())
        assert result["spreadsheet_id"] == "abc123"
        assert result["tab"] == "DropRates"
        assert "fetched_at" in result
        assert result["headers"] == ["itemId", "dropChance"]
        assert result["rows"] == [["1_MB_Sub", "0.35"]]

    def test_fetched_at_is_iso_format(self, tmp_path):
        output_path = tmp_path / "temp_data.json"
        fetch.write_output(
            data={"headers": [], "rows": []},
            spreadsheet_id="x",
            tab_name="y",
            output_path=output_path,
        )
        result = json.loads(output_path.read_text())
        from datetime import datetime
        # Should not raise
        datetime.fromisoformat(result["fetched_at"].replace("Z", "+00:00"))


class TestMainArgs:
    def test_exits_without_args(self):
        with patch("sys.argv", ["fetch.py"]):
            with pytest.raises(SystemExit) as exc_info:
                fetch.main()
        assert exc_info.value.code == 1

    def test_exits_with_one_arg(self):
        with patch("sys.argv", ["fetch.py", "abc123"]):
            with pytest.raises(SystemExit) as exc_info:
                fetch.main()
        assert exc_info.value.code == 1
