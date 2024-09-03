import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from io import BytesIO
import pandas as pd

# Define Google API Scopes
SCOPES = ['https://www.googleapis.com/auth/drive']
DATA_FILE_ID = "11XAt4ezwKcflgqTCCmSDPTDtR29kNGkK"
USERS_DATA_FILE_ID = "1zZQMcdUMkiBdHkmChXq8YD4hQFEglT8w"

# Function to get Google Drive credentials
def get_credentials():
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if creds_path and os.path.exists(os.path.expanduser(creds_path)):
        creds = service_account.Credentials.from_service_account_file(
            os.path.expanduser(creds_path), scopes=SCOPES)
    else:
        raise Exception("Google Drive credentials not found.")
    return creds

# Function to connect to Google Drive API
def connect_to_drive():
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)
    return service

# Function to open a file from Google Drive and return it as a DataFrame
def open_file(file_id=DATA_FILE_ID):
    service = connect_to_drive()
    request = service.files().get_media(fileId=file_id)
    fh = BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    df = pd.read_csv(fh)
    return df

# Function to save (overwrite) a DataFrame to Google Drive
def save_file(df, file_id=DATA_FILE_ID):
    service = connect_to_drive()
    fh = BytesIO()
    df.to_csv(fh, index=False)
    fh.seek(0)
    media = MediaIoBaseUpload(fh, mimetype='text/csv', resumable=True)
    service.files().update(fileId=file_id, media_body=media).execute()
