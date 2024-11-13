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
local_path = "E:/LCN lab backup"  # Path to external drive

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
    filename = filename.replace('<', '').replace('>', '').replace(':', '').replace('"', '')
    filename = filename.replace('/', '').replace('\\', '').replace('|', '').replace('?', '')
    filename = filename.replace('*', '').replace('(', '').replace(')', '').replace(',', '')
    filename = filename.replace('&', '').replace('.', '').replace(';', '')  
    filename = ' '.join(filename.split())  # Remove extra spaces
    return filename[:50]  # Limit to 50 characters

def ensure_path_length(path):
    if len(path) > 250:
        path_parts = path.split(os.sep)
        shortened_parts = [part[:30] if len(part) > 30 else part for part in path_parts]
        return os.sep.join(shortened_parts)
    return path

def file_already_exists(file_path, file_size):
    return os.path.exists(file_path) and os.path.getsize(file_path) == file_size

def download_file(drive_service, file_id, file_name, local_folder_path, mime_type):
    file_name, file_extension = os.path.splitext(file_name)
    file_name = sanitize_filename(file_name)
    file_name += file_extension if file_extension else ".bin"

    file_path_with_extension = os.path.join(local_folder_path, file_name)
    file_path_with_extension = ensure_path_length(file_path_with_extension)

    google_mime_map = {
        'application/vnd.google-apps.document': ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.docx'),
        'application/vnd.google-apps.spreadsheet': ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '.xlsx'),
        'application/vnd.google-apps.presentation': ('application/vnd.openxmlformats-officedocument.presentationml.presentation', '.pptx'),
    }

    try:
        if mime_type in google_mime_map:
            mime_type_export, file_extension = google_mime_map[mime_type]
            request = drive_service.files().export_media(fileId=file_id, mimeType=mime_type_export)
            file_path_with_extension = os.path.join(local_folder_path, file_name) + file_extension
        else:
            request = drive_service.files().get_media(fileId=file_id)

        if os.path.exists(file_path_with_extension):
            print(f"File already exists, skipping download: {file_path_with_extension}")
            return

        file_data = io.BytesIO()
        downloader = MediaIoBaseDownload(file_data, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        with open(file_path_with_extension, 'wb') as f:
            f.write(file_data.getvalue())
        print(f"File saved: {file_path_with_extension}")
    except Exception as e:
        if "exportSizeLimitExceeded" in str(e):
            print(f"Export failed due to size limit. Attempting to download Google-native format for {file_name}.")
            try:
                download_google_native_format(drive_service, file_id, file_name, local_folder_path, mime_type)
            except Exception as link_error:
                print(f"Failed to retrieve Google-native link for {file_name}. Error: {link_error}")
        else:
            print(f"Failed to download {file_name}. Error: {str(e)}")

def download_google_native_format(drive_service, file_id, file_name, local_folder_path, mime_type):
    google_native_extension = {
        'application/vnd.google-apps.document': '.gdoc',
        'application/vnd.google-apps.spreadsheet': '.gsheet',
        'application/vnd.google-apps.presentation': '.gslides',
    }

    file_extension = google_native_extension.get(mime_type, ".unknown")
    file_name = sanitize_filename(file_name) + file_extension
    file_path = os.path.join(local_folder_path, file_name)
    file_path = ensure_path_length(file_path)

    if os.path.exists(file_path):
        print(f"Google-native format file already exists, skipping: {file_path}")
        return

    metadata = drive_service.files().get(fileId=file_id, fields="webViewLink").execute()
    web_link = metadata.get("webViewLink", "No link available")

    try:
        with open(file_path, 'w') as f:
            f.write(f"Google Drive file link (opens in Google Drive): {web_link}")
        print(f"File saved as Google-native link file: {file_path}")
    except Exception as e:
        print(f"Failed to create link file for {file_name}. Error: {str(e)}")

def download_files_in_folder(drive_service, folder_id, local_folder_path, shared_drive_id=None):
    query = f"'{folder_id}' in parents and trashed=false"
    results = drive_service.files().list(
        q=query,
        spaces='drive',
        corpora='user' if shared_drive_id is None else 'drive',
        driveId=shared_drive_id if shared_drive_id else None,
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        fields="nextPageToken, files(id, name, mimeType, size)"
    ).execute()

    items = results.get('files', [])
    for item in items:
        file_id = item['id']
        file_name = item['name']
        mime_type = item['mimeType']
        file_size = int(item.get('size', 0))

        sanitized_folder_name = sanitize_filename(file_name)
        new_folder_path = os.path.join(local_folder_path, sanitized_folder_name)
        new_folder_path = ensure_path_length(new_folder_path)

        if mime_type == 'application/vnd.google-apps.folder':
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
            download_files_in_folder(drive_service, file_id, new_folder_path, shared_drive_id)
        else:
            file_path = os.path.join(local_folder_path, file_name)
            if file_already_exists(file_path, file_size):
                print(f"File already exists, skipping download: {file_path}")
            else:
                download_file(drive_service, file_id, file_name, local_folder_path, mime_type)

def download_shared_drive_files(shared_drive_id):
    creds = Credentials.from_authorized_user_info(info=get_google_auth_user_info())
    drive_service = build('drive', 'v3', credentials=creds)
    download_files_in_folder(drive_service, shared_drive_id, local_path, shared_drive_id)

if __name__ == "__main__":
    shared_drive_id = input("Enter your Shared Drive ID: ")
    download_shared_drive_files(shared_drive_id)
