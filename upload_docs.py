
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
drive = GoogleDrive(gauth)


def upload_to_drive(folder_id,file_name,content):
    file = drive.CreateFile({'parents' : [{'id' : folder_id}], 'title' : file_name})
    file.SetContentString(content)
    file.Upload()

if __name__ == "__main__":
    folder_id = "1d7RhDdxOa1xa-C4Eb7brNuAtrNCXY0aV"
    file_name = "test.txt"
    content = "It is a Test"
    upload_to_drive(folder_id,file_name,content)