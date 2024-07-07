import os
import io
import pickle
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Replace with the path to your client secret JSON file
CLIENT_SECRETS_FILE = "client_secret.json"

# Replace with the scopes required for your application
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Shared Drive ID (replace with your Shared Drive ID)
shared_drive_id = input("YOUR_SHARED_DRIVE_ID")

# Local path for export (current directory)
local_path = os.getcwd()

def get_google_auth_user_info():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds.to_json_info()

def download_shared_drive_files():
    # Set up the Google Drive API client
    GOOGLE_AUTH_USER_INFO = get_google_auth_user_info()
    creds = Credentials.from_authorized_user_info(info=GOOGLE_AUTH_USER_INFO)
    drive_service = build('drive', 'v3', credentials=creds)

    # Function to download files
    def download_file(file_id, file_path, mime_type):
        if mime_type in ['application/vnd.google-apps.spreadsheet', 'application/vnd.oasis.opendocument.spreadsheet']:
            mime_type_export = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif mime_type == 'application/vnd.google-apps.document':
            mime_type_export = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        else:
            mime_type_export = mime_type

        if mime_type_export != mime_type:
            request = drive_service.files().export_media(fileId=file_id, mimeType=mime_type_export)
        else:
            request = drive_service.files().get_media(fileId=file_id)

        file_data = io.BytesIO()
        downloader = MediaIoBaseDownload(file_data, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f'Downloaded {int(status.progress() * 100)}%')

        # Save the file with the appropriate extension
        if mime_type_export == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            file_extension = '.xlsx'
        elif mime_type_export == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            file_extension = '.docx'
        else:
            file_extension = '.' + mime_type_export.split('/')[-1]

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path + file_extension, 'wb') as f:
            f.write(file_data.getvalue())

    # List all files in the Shared Drive
    query = f"'{shared_drive_id}' in parents"
    results = drive_service.files().list(q=query, fields="nextPageToken, files(id, name, mimeType, parents)").execute 
