from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from search_in_opf import search_text_in_opf
import pandas as pd
import subprocess
import uuid

# Load the credentials
credentials = Credentials.from_service_account_file('healthy-terrain-387904-a116ee0eef21.json')
drive_service = build('drive', 'v3', credentials=credentials)


def get_four_digit_uuid():
    # Generate a UUID4 (random) UUID
    generated_uuid = str(uuid.uuid4())

    # Extract the first four characters from the UUID
    four_digit_uuid = generated_uuid[:4]
    return four_digit_uuid

def get_excel(folder_id):
    # Iterate over the objects in the folder
    query = f"'{folder_id}' in parents"
    results = drive_service.files().list(q=query).execute()
    files = results['files']
    download_path = "./data"
    for file in files:
        file_name = file['name']
        file_mime_type = file['mimeType']
        if file_mime_type == 'application/vnd.google-apps.spreadsheet':
            # Export the Google Sheets file as Excel
            file_path = download_path + '/' + file_name + '.xlsx'
            request = drive_service.files().export_media(fileId=file['id'], mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            fh = open(file_path, 'wb')
            downloader = request.execute()
            fh.write(downloader)
            fh.close()
            print(f"Excel file downloaded: {file_name}")
            return file_path

def get_opf_ids(excel_path):
    df = pd.read_excel(excel_path, sheet_name=1)
    column_G_data = df['OPF ID'].dropna().tolist()
    return column_G_data

def download_github_repo(opf_id, opfs_path):
    opf_path = opfs_path+"/"+opf_id
    repo_url =f"https://github.com/OpenPecha-Data/{opf_id}"
    subprocess.call(['git', 'clone', repo_url, opf_path])
    return opf_path

def get_target_text(folder_id):
    results = drive_service.files().list(q=f"'{folder_id}' in parents",fields="files(id, name, mimeType)").execute()
    items = results.get('files', [])
    # Iterate over the items
    for item in items:
        file_id = item['id']
        mime_type = item['mimeType']
        # Check if the file is a Google Docs file
        if mime_type == 'application/vnd.google-apps.document':
            # Export the Google Docs file as plain text
            response = drive_service.files().export(fileId=file_id, mimeType='text/plain').execute()
            content = response.decode('utf-8')
            return content

def get_subfolders(folder_id):
    subfolders = []
    # List all items in the folder with the specified MIME type
    query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    # Iterate over the items
    for item in items:
        subfolder_id = item['id']
        subfolders.append(subfolder_id)
    return subfolders

def create_and_upload_google_docs_file(folder_id, file_name, content):
    # Create a new Google Docs file
    file_metadata = {
        'name': file_name,
        'parents': [folder_id],
        'mimeType': 'application/vnd.google-apps.document'
    }
    created_file = drive_service.files().create(body=file_metadata).execute()
    new_file_id = created_file['id']
    print(f"Created a new Google Docs file '{file_name}' with ID: {new_file_id}")

    # Upload content to the Google Docs file
    media_body = {
        'mimeType': 'text/plain',
        'body': content
    }
    updated_file = drive_service.files().update(fileId=new_file_id, media_body=media_body).execute()
    print(f"Uploaded content to the Google Docs file '{file_name}'")


def main(folder_id):
    excel_path = get_excel(folder_id)
    opf_ids = get_opf_ids(excel_path)
    target_text = get_target_text(folder_id)
    opfs_path = "data/opfs"
    for opf_id in opf_ids:
        opf_path = download_github_repo(opf_id,opfs_path)
        base_text = search_text_in_opf(opf_path,target_text)
        if base_text:
            print(f"Match found in {opf_id}")
            print(base_text)
            file_name = get_four_digit_uuid()
            create_and_upload_google_docs_file(folder_id,file_name,base_text)

if __name__ == "__main__":
    #id = get_subfolders("1nf49zWrdFUQVcI7WRJntJiIZqEVJmgL0")
    folder_id = "1tS3Okfea16P-XfQhzylo7HPS1I8DN1br"
    main(folder_id)