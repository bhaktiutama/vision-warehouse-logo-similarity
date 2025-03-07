import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account

def save_to_spreadsheet(results, spreadsheet_id, range_name, credentials):
    """Save results to Google Spreadsheet."""
    service = build('sheets', 'v4', credentials=credentials)
    
    # Convert results to DataFrame
    df = pd.DataFrame(results)
    
    # Prepare values for sheets
    values = [df.columns.values.tolist()] + df.values.tolist()
    
    body = {
        'values': values
    }
    
    # Update spreadsheet
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()