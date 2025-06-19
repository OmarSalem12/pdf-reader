"""
Spreadsheet export functionality.
"""

import os
import pandas as pd
from typing import List, Dict, Any
from .exceptions import OutputError


class SpreadsheetExporter:
    """Export extracted data to spreadsheet formats."""
    
    def __init__(self):
        """Initialize the exporter."""
        pass
    
    def export(self, data: List[Dict[str, Any]], output_file: str, 
               format_type: str = "excel") -> None:
        """Export data to spreadsheet format.
        
        Args:
            data: List of dictionaries containing extracted fields
            output_file: Path to output file
            format_type: Output format ("excel" or "csv")
            
        Raises:
            OutputError: If export fails
        """
        try:
            # Convert data to DataFrame
            df = self._prepare_dataframe(data)
            
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Export based on format type
            if format_type.lower() == "excel":
                self._export_to_excel(df, output_file)
            elif format_type.lower() == "csv":
                self._export_to_csv(df, output_file)
            else:
                raise OutputError(f"Unsupported format type: {format_type}")
                
        except Exception as e:
            raise OutputError(f"Failed to export data: {e}")
    
    def _prepare_dataframe(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Prepare data for DataFrame conversion.
        
        Args:
            data: List of dictionaries containing extracted fields
            
        Returns:
            Pandas DataFrame with cleaned data
        """
        # Define the columns we want in the output
        columns = [
            "Name", 
            "Date of Birth", 
            "Insurance Information", 
            "Source File", 
            "Extraction Date"
        ]
        
        # Clean and prepare data
        cleaned_data = []
        for item in data:
            cleaned_item = {}
            for col in columns:
                cleaned_item[col] = item.get(col, "")
            
            # Remove raw text and error fields from output
            if "Raw Text" in item:
                del item["Raw Text"]
            if "Error" in item:
                cleaned_item["Error"] = item["Error"]
            
            cleaned_data.append(cleaned_item)
        
        return pd.DataFrame(cleaned_data)
    
    def _export_to_excel(self, df: pd.DataFrame, output_file: str) -> None:
        """Export DataFrame to Excel format.
        
        Args:
            df: Pandas DataFrame to export
            output_file: Path to output Excel file
            
        Raises:
            OutputError: If Excel export fails
        """
        try:
            # Ensure file has .xlsx extension
            if not output_file.endswith('.xlsx'):
                output_file = output_file + '.xlsx'
            
            # Create Excel writer with formatting
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Extracted Data', index=False)
                
                # Get the workbook and worksheet
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
                
                # Add header formatting
                from openpyxl.styles import Font, PatternFill
                header_font = Font(bold=True)
                header_fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
                
                for cell in worksheet[1]:
                    cell.font = header_font
                    cell.fill = header_fill
            
            print(f"Data exported to Excel: {output_file}")
            
        except Exception as e:
            raise OutputError(f"Failed to export to Excel: {e}")
    
    def _export_to_csv(self, df: pd.DataFrame, output_file: str) -> None:
        """Export DataFrame to CSV format.
        
        Args:
            df: Pandas DataFrame to export
            output_file: Path to output CSV file
            
        Raises:
            OutputError: If CSV export fails
        """
        try:
            # Ensure file has .csv extension
            if not output_file.endswith('.csv'):
                output_file = output_file + '.csv'
            
            # Export to CSV
            df.to_csv(output_file, index=False, encoding='utf-8')
            
            print(f"Data exported to CSV: {output_file}")
            
        except Exception as e:
            raise OutputError(f"Failed to export to CSV: {e}")
    
    def export_summary(self, data: List[Dict[str, Any]], output_file: str) -> None:
        """Export a summary report of the extraction process.
        
        Args:
            data: List of dictionaries containing extracted fields
            output_file: Path to output summary file
            
        Raises:
            OutputError: If summary export fails
        """
        try:
            # Calculate summary statistics
            total_files = len(data)
            successful_extractions = sum(1 for item in data if not item.get("Error"))
            failed_extractions = total_files - successful_extractions
            
            # Count fields found
            names_found = sum(1 for item in data if item.get("Name"))
            dobs_found = sum(1 for item in data if item.get("Date of Birth"))
            insurance_found = sum(1 for item in data if item.get("Insurance Information"))
            
            # Create summary DataFrame
            summary_data = {
                "Metric": [
                    "Total Files Processed",
                    "Successful Extractions",
                    "Failed Extractions",
                    "Names Found",
                    "Dates of Birth Found",
                    "Insurance Information Found"
                ],
                "Count": [
                    total_files,
                    successful_extractions,
                    failed_extractions,
                    names_found,
                    dobs_found,
                    insurance_found
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            
            # Export summary
            if output_file.endswith('.xlsx'):
                with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                    
                    # Get the workbook and worksheet
                    workbook = writer.book
                    worksheet = writer.sheets['Summary']
                    
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
                        
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            else:
                summary_df.to_csv(output_file, index=False)
            
            print(f"Summary exported to: {output_file}")
            
        except Exception as e:
            raise OutputError(f"Failed to export summary: {e}") 