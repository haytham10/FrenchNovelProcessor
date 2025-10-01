"""
Google Sheets Integration Module
Handles authentication and spreadsheet creation using Google Sheets API
"""

import os
import pickle
import logging
from typing import List, Dict, Any, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 
          'https://www.googleapis.com/auth/drive.file']


class GoogleSheetsManager:
    """Manages Google Sheets operations"""
    
    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json'):
        """
        Initialize Google Sheets Manager
        
        Args:
            credentials_path: Path to credentials.json file
            token_path: Path to token.json file (OAuth token)
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API using OAuth"""
        # The file token.json stores the user's access and refresh tokens
        if os.path.exists(self.token_path):
            try:
                self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            except Exception as e:
                logger.warning(f"Could not load token.json: {e}")
                logger.info("Deleting token.json and re-authenticating...")
                os.remove(self.token_path)
                self.creds = None
        
        # If there are no (valid) credentials available, let the user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"Warning: Could not refresh token: {e}")
                    print("Deleting token.json and re-authenticating...")
                    if os.path.exists(self.token_path):
                        os.remove(self.token_path)
                    self.creds = None
            
            if not self.creds:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())
        
        # Build the service
        self.service = build('sheets', 'v4', credentials=self.creds)
    
    def create_spreadsheet(self, title: str) -> Dict[str, Any]:
        """
        Create a new Google Spreadsheet
        
        Args:
            title: Title for the spreadsheet
            
        Returns:
            Dictionary containing spreadsheet ID and URL
        """
        try:
            spreadsheet = {
                'properties': {
                    'title': title
                }
            }
            
            spreadsheet = self.service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId,spreadsheetUrl'
            ).execute()
            
            return {
                'spreadsheet_id': spreadsheet.get('spreadsheetId'),
                'spreadsheet_url': spreadsheet.get('spreadsheetUrl')
            }
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            raise
    
    def write_data(self, spreadsheet_id: str, sheet_name: str, data: List[List[Any]], 
                   start_cell: str = 'A1'):
        """
        Write data to a specific sheet
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            sheet_name: Name of the sheet to write to
            data: 2D list of data to write
            start_cell: Starting cell (e.g., 'A1')
        """
        try:
            range_name = f'{sheet_name}!{start_cell}'
            body = {
                'values': data
            }
            
            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            raise
    
    def create_sheet(self, spreadsheet_id: str, sheet_name: str, 
                     row_count: int = 1000, column_count: int = 26):
        """
        Add a new sheet to an existing spreadsheet
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            sheet_name: Name for the new sheet
            row_count: Number of rows
            column_count: Number of columns
        """
        try:
            requests = [{
                'addSheet': {
                    'properties': {
                        'title': sheet_name,
                        'gridProperties': {
                            'rowCount': row_count,
                            'columnCount': column_count
                        }
                    }
                }
            }]
            
            body = {
                'requests': requests
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            raise
    
    def format_sheet(self, spreadsheet_id: str, sheet_id: int, formatting_requests: List[Dict]):
        """
        Apply formatting to a sheet
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            sheet_id: The ID of the sheet (not the name)
            formatting_requests: List of formatting request dictionaries
        """
        try:
            body = {
                'requests': formatting_requests
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            raise
    
    def get_sheet_id(self, spreadsheet_id: str, sheet_name: str) -> Optional[int]:
        """
        Get the sheet ID for a given sheet name
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            sheet_name: Name of the sheet
            
        Returns:
            Sheet ID or None if not found
        """
        try:
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            for sheet in spreadsheet.get('sheets', []):
                if sheet['properties']['title'] == sheet_name:
                    return sheet['properties']['sheetId']
            
            return None
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            raise
    
    def set_column_widths(self, spreadsheet_id: str, sheet_id: int, 
                          column_widths: Dict[int, int]):
        """
        Set column widths
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            sheet_id: The ID of the sheet
            column_widths: Dictionary mapping column index (0-based) to width in pixels
        """
        requests = []
        for col_index, width in column_widths.items():
            requests.append({
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': 'COLUMNS',
                        'startIndex': col_index,
                        'endIndex': col_index + 1
                    },
                    'properties': {
                        'pixelSize': width
                    },
                    'fields': 'pixelSize'
                }
            })
        
        if requests:
            self.format_sheet(spreadsheet_id, sheet_id, requests)

    def set_row_heights(self, spreadsheet_id: str, sheet_id: int,
                         start_row: int, end_row: int, pixel_size: int):
        """
        Set a fixed row height for a range of rows.

        Args:
            spreadsheet_id: Spreadsheet ID
            sheet_id: Target sheet ID
            start_row: Zero-based start row index (inclusive)
            end_row: Zero-based end row index (exclusive)
            pixel_size: Row height in pixels
        """
        request = [{
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'ROWS',
                    'startIndex': start_row,
                    'endIndex': end_row
                },
                'properties': {
                    'pixelSize': pixel_size
                },
                'fields': 'pixelSize'
            }
        }]
        self.format_sheet(spreadsheet_id, sheet_id, request)

    def set_wrap_strategy(self, spreadsheet_id: str, sheet_id: int,
                           start_row: int, end_row: int,
                           start_col: int, end_col: int,
                           strategy: str = 'CLIP'):
        """
        Set text wrap strategy for a rectangular range.

        strategy values: 'OVERFLOW_CELL', 'CLIP', or 'WRAP'.
        """
        request = [{
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': start_row,
                    'endRowIndex': end_row,
                    'startColumnIndex': start_col,
                    'endColumnIndex': end_col
                },
                'cell': {
                    'userEnteredFormat': {
                        'wrapStrategy': strategy,
                        'verticalAlignment': 'MIDDLE'
                    }
                },
                'fields': 'userEnteredFormat.wrapStrategy,userEnteredFormat.verticalAlignment'
            }
        }]
        self.format_sheet(spreadsheet_id, sheet_id, request)
    
    def freeze_rows(self, spreadsheet_id: str, sheet_id: int, num_rows: int = 1):
        """
        Freeze header rows
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            sheet_id: The ID of the sheet
            num_rows: Number of rows to freeze
        """
        requests = [{
            'updateSheetProperties': {
                'properties': {
                    'sheetId': sheet_id,
                    'gridProperties': {
                        'frozenRowCount': num_rows
                    }
                },
                'fields': 'gridProperties.frozenRowCount'
            }
        }]
        
        self.format_sheet(spreadsheet_id, sheet_id, requests)
    
    def apply_header_formatting(self, spreadsheet_id: str, sheet_id: int, 
                                num_columns: int, bg_color: Dict[str, float]):
        """
        Apply formatting to header row
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            sheet_id: The ID of the sheet
            num_columns: Number of columns in header
            bg_color: Background color as RGB dict (e.g., {'red': 0.27, 'green': 0.45, 'blue': 0.77})
        """
        requests = [
            {
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': num_columns
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': bg_color,
                            'textFormat': {
                                'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                                'bold': True,
                                'fontSize': 11
                            },
                            'horizontalAlignment': 'CENTER',
                            'verticalAlignment': 'MIDDLE'
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)'
                }
            }
        ]
        
        self.format_sheet(spreadsheet_id, sheet_id, requests)
    
    def apply_alternating_row_colors(self, spreadsheet_id: str, sheet_id: int,
                                     num_rows: int, num_columns: int,
                                     color1: Dict[str, float], color2: Dict[str, float]):
        """
        Apply alternating row colors
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            sheet_id: The ID of the sheet
            num_rows: Total number of rows
            num_columns: Number of columns
            color1: First color (RGB dict)
            color2: Second color (RGB dict)
        """
        requests = []
        
        for row in range(1, num_rows):  # Start from 1 to skip header
            color = color1 if row % 2 == 1 else color2
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': row,
                        'endRowIndex': row + 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': num_columns
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': color
                        }
                    },
                    'fields': 'userEnteredFormat.backgroundColor'
                }
            })
        
        if requests:
            self.format_sheet(spreadsheet_id, sheet_id, requests)
    
    def apply_borders(self, spreadsheet_id: str, sheet_id: int, 
                     num_rows: int, num_columns: int):
        """
        Apply borders to all cells
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            sheet_id: The ID of the sheet
            num_rows: Total number of rows
            num_columns: Number of columns
        """
        border_style = {
            'style': 'SOLID',
            'width': 1,
            'color': {'red': 0.82, 'green': 0.82, 'blue': 0.82}
        }
        
        requests = [{
            'updateBorders': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 0,
                    'endRowIndex': num_rows,
                    'startColumnIndex': 0,
                    'endColumnIndex': num_columns
                },
                'top': border_style,
                'bottom': border_style,
                'left': border_style,
                'right': border_style,
                'innerHorizontal': border_style,
                'innerVertical': border_style
            }
        }]
        
        self.format_sheet(spreadsheet_id, sheet_id, requests)
