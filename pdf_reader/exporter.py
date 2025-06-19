"""Data export functionality for PDF Reader package."""

import csv
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .exceptions import ExportError

logger = logging.getLogger(__name__)


class DataExporter:
    """Export extracted data to various formats."""

    def __init__(self, output_directory: Optional[str] = None):
        """Initialize data exporter.

        Args:
            output_directory: Directory to save exported files
        """
        self.output_directory = (
            Path(output_directory) if output_directory else Path.cwd()
        )
        self.output_directory.mkdir(parents=True, exist_ok=True)

    def export_to_csv(
        self, data: List[Dict[str, Any]], filename: Optional[str] = None
    ) -> str:
        """Export data to CSV format.

        Args:
            data: List of dictionaries containing extracted data
            filename: Output filename (optional)

        Returns:
            Path to exported CSV file

        Raises:
            ExportError: If export fails
        """
        if not data:
            raise ExportError("No data to export")

        if filename is None:
            filename = "extracted_data.csv"
        elif not filename.endswith(".csv"):
            filename += ".csv"

        file_path = self.output_directory / filename

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = list(data[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

            logger.info("Data exported to CSV: %s", file_path)
            return str(file_path)

        except Exception as e:
            error_msg = f"Failed to export to CSV: {e}"
            logger.error(error_msg)
            raise ExportError(error_msg, format_type="csv", output_path=str(file_path))

    def export_to_excel(
        self, data: List[Dict[str, Any]], filename: Optional[str] = None
    ) -> str:
        """Export data to Excel format.

        Args:
            data: List of dictionaries containing extracted data
            filename: Output filename (optional)

        Returns:
            Path to exported Excel file

        Raises:
            ExportError: If export fails
        """
        if not data:
            raise ExportError("No data to export")

        try:
            from openpyxl import Workbook
        except ImportError:
            raise ExportError(
                "openpyxl is required for Excel export. \
                Install with: pip install openpyxl"
            )

        if filename is None:
            filename = "extracted_data.xlsx"
        elif not filename.endswith(".xlsx"):
            filename += ".xlsx"

        file_path = self.output_directory / filename

        try:
            wb = Workbook()
            ws = wb.active
            if ws is None:
                raise ExportError("Failed to create worksheet")
            ws.title = "Extracted Data"

            if data:
                # Write headers
                headers = list(data[0].keys())
                for col, header in enumerate(headers, 1):
                    ws.cell(row=1, column=col, value=header)

                # Write data
                for row, record in enumerate(data, 2):
                    for col, header in enumerate(headers, 1):
                        value = record.get(header, "")
                        ws.cell(row=row, column=col, value=value)

            wb.save(file_path)
            logger.info("Data exported to Excel: %s", file_path)
            return str(file_path)

        except Exception as e:
            error_msg = f"Failed to export to Excel: {e}"
            logger.error(error_msg)
            raise ExportError(
                error_msg, format_type="excel", output_path=str(file_path)
            )

    def export_to_json(
        self, data: List[Dict[str, Any]], filename: Optional[str] = None
    ) -> str:
        """Export data to JSON format.

        Args:
            data: List of dictionaries containing extracted data
            filename: Output filename (optional)

        Returns:
            Path to exported JSON file

        Raises:
            ExportError: If export fails
        """
        if not data:
            raise ExportError("No data to export")

        if filename is None:
            filename = "extracted_data.json"
        elif not filename.endswith(".json"):
            filename += ".json"

        file_path = self.output_directory / filename

        try:
            import json

            with open(file_path, "w", encoding="utf-8") as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False)

            logger.info("Data exported to JSON: %s", file_path)
            return str(file_path)

        except Exception as e:
            error_msg = f"Failed to export to JSON: {e}"
            logger.error(error_msg)
            raise ExportError(error_msg, format_type="json", output_path=str(file_path))

    def export_data(
        self,
        data: List[Dict[str, Any]],
        output_path: str,
        format_type: str = "csv",
    ) -> str:
        """Export data to specified format.

        Args:
            data: List of dictionaries containing extracted data
            output_path: Output file path
            format_type: Export format ('csv', 'excel', 'json')

        Returns:
            Path to exported file

        Raises:
            ExportError: If export fails or format is unsupported
        """
        format_type = format_type.lower()

        # Extract filename from output_path
        filename = Path(output_path).name

        if format_type == "csv":
            return self.export_to_csv(data, filename)
        elif format_type == "excel":
            return self.export_to_excel(data, filename)
        elif format_type == "json":
            return self.export_to_json(data, filename)
        else:
            raise ExportError(f"Unsupported export format: {format_type}")

    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats.

        Returns:
            List of supported format names
        """
        return ["csv", "excel", "json"]

    def validate_data(self, data: Any) -> bool:
        """Validate data before export.

        Args:
            data: Data to validate

        Returns:
            True if data is valid for export
        """
        if not isinstance(data, list):
            logger.error("Data must be a list of dictionaries")
            return False

        if not data:
            logger.warning("No data to export")
            return False

        for i, record in enumerate(data):
            if not isinstance(record, dict):
                logger.error("Record %d is not a dictionary", i)
                return False

        return True
