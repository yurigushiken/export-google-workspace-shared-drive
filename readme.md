# Google Workspace Shared Drive Modified Export Script

This script allows you to export all files from a Google Workspace Shared Drive to your local machine. As of November 2024, Google Workspace does not provide a direct way to export Shared Drive content, so this script fills this gap.

Thank you 'fariazz' for the original script.

This modified script addresses files with paths that are too long, invalid file name characters, or in export size limit excess. 
In the event an export is interrupted, this modified script will check for a file before re-exporting, so as to not have to re-export files that have already been saved. 

Improvements in this project:

- Enhanced filename sanitization removes additional special characters, limits filenames to 50 characters, and ensures cleaner, compatible filenames (cause for errors when downloading zipped in browser).
- Introduces path length handling to truncate folder and file names, avoiding issues with excessively long paths.
- Checks file size in addition to file existence to prevent redownloading incomplete or modified files.
- Handles Google-native formats with a fallback mechanism to generate web view links when export size limits are exceeded.
- Incorporates improved error handling with specific messages for issues like export size limits and alternative actions for problematic files.
- Optimizes duplicate file avoidance by comparing file names and sizes more effectively.



# Step-by-Step Instructions for Setting Up and Running the Google Drive Backup Script (Oct 24)
---

## 1. Prerequisites

Before you start, ensure the following:

- **Python Installed**: Python 3.6 or higher installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
- **Google Cloud Project**: Access to the [Google Cloud Console](https://console.cloud.google.com/) to enable the Google Drive API and create credentials.
- **GitHub Repository**: Download the script from the repository.
- **Required Python Libraries**:
  - Install libraries using `pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client`.

---

## 2. Setting Up Google Cloud Project

### Step 2.1: Create a New Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click on the project dropdown in the top-left corner.
3. Select **New Project** and provide a name (e.g., `DriveBackupProject`).
4. Click **Create**.

### Step 2.2: Enable the Google Drive API
1. In your project, navigate to **APIs & Services > Library**.
2. Search for "Google Drive API" and click on it.
3. Click **Enable**.

### Step 2.3: Create OAuth 2.0 Credentials
1. Go to **APIs & Services > Credentials**.
2. Click **Create Credentials** > **OAuth Client ID**.
3. You may need to configure the OAuth Consent Screen:
   - Select **External** for testing purposes.
   - Add a name under "App Information" (e.g., `Drive Backup`).
   - Add your email in the "User Support Email" field.
   - Add "https://www.googleapis.com/auth/drive" as a scope.
   - Save and continue.
4. After configuring the OAuth screen, return to **Create Credentials** > **OAuth Client ID**.
   - Set the application type to **Desktop app**.
   - Click **Create**.
5. Download the `client_secret.json` file and place it in the same directory as the script.

---

## 3. Preparing the Script

### Step 3.1: Clone or Download the GitHub Repository
1. Visit the repository: [GitHub Link](https://github.com/fariazz/export-google-workspace-shared-drive).
2. Download the repository as a ZIP file or clone it using:
   ```bash
   git clone https://github.com/fariazz/export-google-workspace-shared-drive.git
   ```
3. Navigate to the folder containing the script:
   ```bash
   cd export-google-workspace-shared-drive
   ```

### Step 3.2: Install Python Libraries
Run the following command in the terminal to install dependencies:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Step 3.3: Update the Script
1. Place the `client_secret.json` file in the same folder as the `script.py` file.
2. Ensure the local path for backups is correctly set in the script. For example:
   ```python
   local_path = "E:/test"  # Path to your external hard drive or preferred folder
   ```

---

## 4. Running the Script

1. Open a terminal (or VS Code terminal) and navigate to the script folder.
2. Run the script:
   ```bash
   python script.py
   ```
3. When prompted, enter the **Shared Drive ID** or the ID of the folder you want to back up. The ID can be found in the URL of the Google Drive folder:
   - Example: `https://drive.google.com/drive/folders/{FOLDER_ID}`

4. A browser window will open, asking you to log in and authorize access. After authorizing, the script will begin downloading files.

---

## 5. Common Errors and Fixes

### Error: "Path Too Long"
- **Cause**: Windows path length exceeds 260 characters.
- **Fix**: The script now truncates folder and file names to 50 characters to avoid this issue.

### Error: "Invalid Characters in File Name"
- **Cause**: Some file names contain invalid characters (`<`, `>`, `:`, etc.).
- **Fix**: The script automatically removes or replaces invalid characters.

### Error: "File Too Large to Export"
- **Cause**: Google-native files exceed export size limits.
- **Fix**: The script attempts to save these files as Google-native formats (e.g., `.gdoc`, `.gsheet`).

### Error: "File Not Found"
- **Cause**: The file was deleted, moved, or inaccessible.
- **Fix**: The script logs the error and continues with the next file.

---

## 6. Verifying Progress

The script skips files that already exist and matches their size. If the script is interrupted, you can re-run it to continue from where it left off.

---

## 7. Troubleshooting

- **Log Files**: Modify the script to write logs for skipped or failed files for later review.
- **Permissions**: Ensure you have the correct permissions for all files in the shared drive or folder.
- **Google API Quota**: If you hit Google API quota limits, wait for the quota to reset (usually 24 hours).

---

These detailed steps, along with the error-handling changes in the script, should ensure a smooth backup process.

This script has only been tested on Windows 11.
