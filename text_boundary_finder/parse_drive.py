from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from search_in_opf import search_text_in_opf
import subprocess
import pandas as pd


# Load the credentials
credentials = Credentials.from_service_account_file('credentials.json')
drive_service = build('drive', 'v3', credentials=credentials)


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
            request = drive_service.files().export(fileId=file['id'], mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response = request.execute()
            with open(file_path, 'wb') as file:
                file.write(response)
            print(f"Excel file downloaded: {file_name}")
            return file_path
        elif file_mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            # Download the existing Excel file
            file_path = download_path + '/' + file_name
            request = drive_service.files().get_media(fileId=file['id'])
            response = request.execute()
            with open(file_path, 'wb') as file:
                file.write(response)
            print(f"Excel file downloaded: {file_name}")
            return file_path

def get_opf_ids(excel_path):
    # Read the Excel file into a DataFrame
    df = pd.read_excel(excel_path, sheet_name=1)  # Assuming the data is in the second sheet
    
    # Extract the OPF IDs from column G
    column_G_data = df.iloc[:, 6].dropna().tolist()
    
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

def create_subfolder_and_docs(folder_id, subfolder_name, doc_title, doc_content):
    # Authenticate and create a Drive service instance
    credentials = Credentials.from_service_account_file('credentials.json')
    drive_service = build('drive', 'v3', credentials=credentials)

    # Check if the subfolder already exists
    query = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and name = '{subfolder_name}'"
    response = drive_service.files().list(q=query).execute()
    subfolders = response.get('files', [])

    if not subfolders:
        # Create the subfolder
        subfolder_metadata = {
            'name': subfolder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [folder_id]
        }
        subfolder = drive_service.files().create(body=subfolder_metadata).execute()
        subfolder_id = subfolder['id']
    else:
        subfolder_id = subfolders[0]['id']

    # Create the Google Docs file within the subfolder
    doc_service = build('docs', 'v1', credentials=credentials)
    doc_metadata = {
        'title': doc_title
    }
    doc = doc_service.documents().create(body=doc_metadata).execute()
    doc_id = doc['documentId']

    # Move the created document to the subfolder
    drive_service.files().update(
        fileId=doc_id,
        addParents=subfolder_id,
        fields='id'
    ).execute()

    # Insert content into the Google Docs file
    doc_service.documents().batchUpdate(
        documentId=doc_id,
        body={
            'requests': [
                {
                    'insertText': {
                        'location': {
                            'index': 1
                        },
                        'text': doc_content
                    }
                }
            ]
        }
    ).execute()

    return doc_id


def main(folder_id):
    excel_path = get_excel(folder_id)
    opf_ids = get_opf_ids(excel_path)
    target_text = get_target_text(folder_id)
    opfs_path = "data/opfs"
    for opf_id in opf_ids:
        try:
            opf_path = download_github_repo(opf_id,opfs_path)
            base_text = search_text_in_opf(opf_path,target_text)
        except:
            continue
        if base_text:
            print(f"Match found in {opf_id}")
            print(base_text)
            create_subfolder_and_docs(folder_id,"OCR",f"OCR_{opf_id}",base_text)

if __name__ == "__main__":
    #id = get_subfolders("1nf49zWrdFUQVcI7WRJntJiIZqEVJmgL0")
    folder_id = "1d7RhDdxOa1xa-C4Eb7brNuAtrNCXY0aV"
    create_subfolder_and_docs(folder_id,"OCR","text_file","content of text")
    #main(folder_id)