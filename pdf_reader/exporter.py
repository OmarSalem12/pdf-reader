"""
Data export utilities for PDF extracted data.

This module provides functionality to export extracted PDF data to various formats
including Excel spreadsheets and CSV files.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd

from .exceptions import ExportError

logger = logging.getLogger(__name__)


class DataExporter:
    """
    A class for exporting extracted PDF data to various formats.
    
    This class provides methods to export structured data extracted from PDFs
    to Excel spreadsheets and CSV files with proper formatting and organization.
    
    Attributes:
        output_dir (Path): Directory where exported files will be saved
        timestamp_format (str): Format string for timestamps in filenames
    """
    
    def __init__(self, output_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the DataExporter with output directory.
        
        Args:
            output_dir: Directory where exported files will be saved.
                       If None, uses current working directory
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.timestamp_format = "%Y%m%d_%H%M%S"
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("DataExporter initialized with output directory: %s", self.output_dir)
    
    def export_to_excel(self, data: List[Dict], filename: Optional[str] = None) -> str:
        """
        Export extracted data to an Excel spreadsheet.
        
        Args:
            data: List of dictionaries containing extracted data
            filename: Optional filename for the Excel file.
                     If None, generates a timestamped filename
                     
        Returns:
            Path to the created Excel file
            
        Raises:
            ExportError: If data is invalid or export fails
        """
        if not data:
            error_msg = "Cannot export empty data list"
            logger.error(error_msg)
            raise ExportError(error_msg)
        
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            error_msg = "Data must be a list of dictionaries"
            logger.error(error_msg)
            raise ExportError(error_msg)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime(self.timestamp_format)
            filename = f"pdf_extracted_data_{timestamp}.xlsx"
        
        # Ensure filename has .xlsx extension
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        filepath = self.output_dir / filename
        
        try:
            logger.info("Exporting %d records to Excel file: %s", len(data), filepath)
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Add metadata
            metadata = {
                'Export Date': datetime.now().isoformat(),
                'Total Records': len(data),
                'Source': 'PDF Reader Package'
            }
            
            # Create Excel writer with formatting
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Write main data
                df.to_excel(writer, sheet_name='Extracted Data', index=False)
                
                # Write metadata
                metadata_df = pd.DataFrame([metadata])
                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
                
                # Get workbook and worksheet for formatting
                workbook = writer.book
                worksheet = writer.sheets['Extracted Data']
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            logger.info("Successfully exported data to Excel file: %s", filepath)
            return str(filepath)
            
        except Exception as e:
            error_msg = f"Failed to export data to Excel: {e}"
            logger.error(error_msg)
            raise ExportError(error_msg) from e
    
    def export_to_csv(self, data: List[Dict], filename: Optional[str] = None) -> str:
        """
        Export extracted data to a CSV file.
        
        Args:
            data: List of dictionaries containing extracted data
            filename: Optional filename for the CSV file.
                     If None, generates a timestamped filename
                     
        Returns:
            Path to the created CSV file
            
        Raises:
            ExportError: If data is invalid or export fails
        """
        if not data:
            error_msg = "Cannot export empty data list"
            logger.error(error_msg)
            raise ExportError(error_msg)
        
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            error_msg = "Data must be a list of dictionaries"
            logger.error(error_msg)
            raise ExportError(error_msg)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime(self.timestamp_format)
            filename = f"pdf_extracted_data_{timestamp}.csv"
        
        # Ensure filename has .csv extension
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        filepath = self.output_dir / filename
        
        try:
            logger.info("Exporting %d records to CSV file: %s", len(data), filepath)
            
            # Convert to DataFrame and export
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            logger.info("Successfully exported data to CSV file: %s", filepath)
            return str(filepath)
            
        except Exception as e:
            error_msg = f"Failed to export data to CSV: {e}"
            logger.error(error_msg)
            raise ExportError(error_msg) from e
    
    def export_multiple_formats(self, data: List[Dict], base_filename: Optional[str] = None) -> Dict[str, str]:
        """
        Export data to multiple formats (Excel and CSV).
        
        Args:
            data: List of dictionaries containing extracted data
            base_filename: Optional base filename (without extension).
                          If None, generates a timestamped filename
                          
        Returns:
            Dictionary mapping format names to file paths
            
        Raises:
            ExportError: If data is invalid or export fails
        """
        if not data:
            error_msg = "Cannot export empty data list"
            logger.error(error_msg)
            raise ExportError(error_msg)
        
        # Generate base filename if not provided
        if not base_filename:
            timestamp = datetime.now().strftime(self.timestamp_format)
            base_filename = f"pdf_extracted_data_{timestamp}"
        
        results = {}
        
        try:
            # Export to Excel
            excel_filename = f"{base_filename}.xlsx"
            results['excel'] = self.export_to_excel(data, excel_filename)
            
            # Export to CSV
            csv_filename = f"{base_filename}.csv"
            results['csv'] = self.export_to_csv(data, csv_filename)
            
            logger.info("Successfully exported data to multiple formats: %s", list(results.keys()))
            return results
            
        except Exception as e:
            error_msg = f"Failed to export data to multiple formats: {e}"
            logger.error(error_msg)
            raise ExportError(error_msg) from e
    
    def get_export_summary(self, data: List[Dict]) -> Dict:
        """
        Generate a summary of the data to be exported.
        
        Args:
            data: List of dictionaries containing extracted data
            
        Returns:
            Dictionary containing summary information
            
        Raises:
            ExportError: If data is invalid
        """
        if not data:
            error_msg = "Cannot generate summary for empty data"
            logger.error(error_msg)
            raise ExportError(error_msg)
        
        try:
            df = pd.DataFrame(data)
            
            summary = {
                'total_records': len(data),
                'fields': list(df.columns),
                'field_count': len(df.columns),
                'non_null_counts': df.count().to_dict(),
                'export_timestamp': datetime.now().isoformat()
            }
            
            logger.debug("Generated export summary: %s", summary)
            return summary
            
        except Exception as e:
            error_msg = f"Failed to generate export summary: {e}"
            logger.error(error_msg)
            raise ExportError(error_msg) from e
    
    def set_output_directory(self, output_dir: Union[str, Path]) -> None:
        """
        Set a new output directory for exports.
        
        Args:
            output_dir: New directory path for exports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Output directory changed to: %s", self.output_dir) 