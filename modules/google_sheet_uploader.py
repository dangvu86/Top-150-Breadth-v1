"""
Google Sheet Uploader Module
Automatically uploads market breadth data to Google Sheets
"""
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
from datetime import datetime


def get_google_sheets_client():
    """
    Create Google Sheets client using service account credentials from Streamlit secrets

    Returns:
        gspread.Client: Authenticated Google Sheets client
    """
    try:
        # Get credentials from Streamlit secrets
        credentials_dict = st.secrets["gcp_service_account"]

        # Define the scope
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        # Create credentials
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=scope
        )

        # Authorize and return client
        client = gspread.authorize(credentials)
        return client

    except Exception as e:
        st.warning(f"Cannot connect to Google Sheets: {str(e)}")
        return None


def upload_to_google_sheet(df, sheet_id, worksheet_name="Market Breadth Data"):
    """
    Upload dataframe to Google Sheet with same formatting as display table

    Args:
        df: DataFrame to upload (already formatted with display names and string values)
        sheet_id: Google Sheet ID
        worksheet_name: Name of the worksheet to update

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get Google Sheets client
        client = get_google_sheets_client()
        if client is None:
            return False

        # Open the spreadsheet
        spreadsheet = client.open_by_key(sheet_id)

        # Calculate required size (add small buffer)
        required_rows = len(df) + 5  # +5 for header and buffer
        required_cols = len(df.columns)

        # Try to get existing worksheet or create new one
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            # Clear existing data
            worksheet.clear()
            # Resize worksheet to fit data
            worksheet.resize(rows=required_rows, cols=required_cols)
        except gspread.exceptions.WorksheetNotFound:
            # Create new worksheet if not exists
            worksheet = spreadsheet.add_worksheet(
                title=worksheet_name,
                rows=required_rows,
                cols=required_cols
            )

        # Fill NaN values with empty string before converting to list
        df_clean = df.fillna('')

        # Convert dataframe to list of lists for gspread
        # Include header
        data = [df_clean.columns.tolist()] + df_clean.values.tolist()

        # Update worksheet with data (USER_ENTERED preserves string formatting)
        worksheet.update(data, value_input_option='USER_ENTERED')

        return True

    except Exception as e:
        st.error(f"Failed to upload to Google Sheet: {str(e)}")
        return False


def format_google_sheet(sheet_id, worksheet_name="Market Breadth Data"):
    """
    Apply formatting to Google Sheet (optional - for better presentation)

    Args:
        sheet_id: Google Sheet ID
        worksheet_name: Name of the worksheet to format
    """
    try:
        client = get_google_sheets_client()
        if client is None:
            return

        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.worksheet(worksheet_name)

        # Format header row (bold, freeze)
        worksheet.format('1:1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        })

        # Freeze header row
        worksheet.freeze(rows=1)

        # Auto-resize columns
        worksheet.columns_auto_resize(0, len(worksheet.row_values(1)))

    except Exception as e:
        # Silent fail for formatting errors
        pass
