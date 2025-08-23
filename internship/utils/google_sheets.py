import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_sheet(sheet_name="InternshipApplications"):
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "config/credentials.json", scope
    )
    client = gspread.authorize(creds)
    sheet = client.open("Internship Applications").worksheet(sheet_name)
    return sheet
