Thank you to fariazz for the original script.

Improvements in this project:

- Enhanced filename sanitization removes additional special characters, limits filenames to 50 characters, and ensures cleaner, compatible filenames.
- Introduces path length handling to truncate folder and file names, avoiding issues with excessively long paths.
- Checks file size in addition to file existence to prevent redownloading incomplete or modified files.
- Handles Google-native formats with a fallback mechanism to generate web view links when export size limits are exceeded.
- Incorporates improved error handling with specific messages for issues like export size limits and alternative actions for problematic files.
- Optimizes duplicate file avoidance by comparing file names and sizes more effectively.

# Google Workspace Shared Drive Export Script

This script allows you to export all files from a Google Workspace Shared Drive to your local machine. As of October 2024, Google Workspace does not provide a direct way to export Shared Drive content, so this script fills that gap.


## Prerequisites

1. Python 3.6 or higher
2. Google Cloud SDK
3. Google Drive API enabled in your Google Cloud project
4. Client secret JSON file from your Google Cloud project

## Setup Instructions

### Step 1: Enable Google Drive API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing project.
3. Navigate to **API & Services > Library**.
4. Search for "Google Drive API" and click **Enable**.

### Step 2: Create OAuth 2.0 Client ID

1. In the Google Cloud Console, go to **API & Services > Credentials**.
2. Click on **Create Credentials** and select **OAuth 2.0 Client ID** (select User not Application if prompted).
3. When asked about scopes, add **https://www.googleapis.com/auth/drive.readonly**
4. Set the application type to **Desktop app**.
5. Download the `client_secret.json` file and save it in the same directory as the script.

### Step 3: Install Required Python Packages

```sh
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Step 4: Run it
```sh
python script.py
```

The Shared Drive ID can be obtained from the URL of the root folder of the Shared Drive, e.g. `https://drive.google.com/drive/u/1/folders/{ID FOUND HERE}` 

### Compatibility

This script has only been tested on Windows 11.
