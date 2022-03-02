import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json


# use creds to create a client to interact with the Google Drive API
scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'Json/googleapi.json')
config = json.load(open(filename))
creds = ServiceAccountCredentials.from_json_keyfile_name(filename, scope)
client = gspread.authorize(creds)



# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
spreadsheet = client.open("Test Binance")

# Extract and print all of the values

def readcolumn(parameter,sh):
  sheet = spreadsheet.get_worksheet(sh)
  return sheet.col_values(parameter)

def readrow(parameter,sh):
  sheet = spreadsheet.get_worksheet(sh)
  return sheet.row_values(parameter)

def update(start,_list,sh):
  sheet = spreadsheet.get_worksheet(sh)
  return sheet.update(start,_list)

def cellvalue(x,y,sh):
  sheet = spreadsheet.get_worksheet(sh)
  return sheet.cell(x,y).value

def find(findme,sh):
  sheet = spreadsheet.get_worksheet(sh)
  findme = str(findme)
  cell = sheet.find(findme)
  if cell is None :
    return "false"
  else:
    array = [cell.row, cell.col]
    return array
