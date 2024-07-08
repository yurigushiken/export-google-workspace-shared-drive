import os
import io
import json
import pickle
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/drive']
local_path = os.path.join(os.getcwd(), "exports")

if not os.path.exists(local_path):
    os.makedirs(local_path)

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
    creds_json = creds.to_json()
    return json.loads(creds_json)

def sanitize_filename(filename):
    # Replace slashes and other problematic characters
    filename = filename.replace('<', '-').replace('>', '-').replace(':', '-').replace('"', '-').replace('/', '-').replace('\\', '-').replace('|', '-').replace('?', '-').replace('*', '-').replace('(', '-').replace(')', '-').replace(',', '-')
    filename = (filename[:255]) if len(filename) > 255 else filename
    return filename

def download_file(drive_service, file_id, file_name, local_folder_path, mime_type):

    file_name = sanitize_filename(file_name)

    # Mapping for Google Drive document types to Microsoft Office formats
    google_mime_map = {
        'application/vnd.google-apps.document': ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.docx'),
        'application/vnd.google-apps.spreadsheet': ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '.xlsx'),
        'application/vnd.google-apps.presentation': ('application/vnd.openxmlformats-officedocument.presentationml.presentation', '.pptx'),
    }

    # Check if the file is a Google Docs type and needs conversion
    if mime_type in google_mime_map:
        mime_type_export, file_extension = google_mime_map[mime_type]
        request = drive_service.files().export_media(fileId=file_id, mimeType=mime_type_export)
    else:
        # Preserve original file extension by extracting from MIME type or default to a general type
        file_extension = '.' + mime_type.split('/')[-1].split(';')[0] if '/' in mime_type else '.bin'
        request = drive_service.files().get_media(fileId=file_id)

    # Append file extension if not already present, or if a conversion extension has been specified
    if not file_name.lower().endswith(file_extension):
        file_name += file_extension

    file_path_with_extension = os.path.join(local_folder_path, file_name)
    os.makedirs(os.path.dirname(file_path_with_extension), exist_ok=True)

    file_data = io.BytesIO()
    downloader = MediaIoBaseDownload(file_data, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

    with open(file_path_with_extension, 'wb') as f:
        f.write(file_data.getvalue())
    print(f"File saved: {file_path_with_extension}")


def download_files_in_folder(drive_service, folder_id, local_folder_path, shared_drive_id):
    query = f"'{folder_id}' in parents and trashed=false"
    results = drive_service.files().list(
        q=query,
        spaces='drive',
        corpora='drive',
        driveId=shared_drive_id,
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        fields="nextPageToken, files(id, name, mimeType)"
    ).execute()

    items = results.get('files', [])
    for item in items:
        file_id = item['id']
        file_name = item['name']
        mime_type = item['mimeType']
        if mime_type == 'application/vnd.google-apps.folder':
            new_folder_path = os.path.join(local_folder_path, sanitize_filename(file_name))
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
            download_files_in_folder(drive_service, file_id, new_folder_path, shared_drive_id)
        else:
            download_file(drive_service, file_id, file_name, local_folder_path, mime_type)

def download_shared_drive_files(shared_drive_id):
    creds = Credentials.from_authorized_user_info(info=get_google_auth_user_info())
    drive_service = build('drive', 'v3', credentials=creds)
    download_files_in_folder(drive_service, shared_drive_id, local_path, shared_drive_id)

if __name__ == "__main__":
    shared_drive_id = input("Enter your Shared Drive ID: ")
    download_shared_drive_files(shared_drive_id)
