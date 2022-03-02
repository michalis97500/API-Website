import requests
import json
import PyPDF2
import os

uri = 'https://api2.hiveos.farm/api/v2'
contype = "application/json"
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'Json/hive.json')
config = json.load(open(filename))
token = 'Bearer ' + config["token"]


def account():
    url = "{}/account".format(uri)
    payload = {}
    headers = {
        "Content-Type": contype,
        'Authorization': token
    }
    response = requests.request("GET", url, headers=headers, params=payload)
    return json.loads(response.text)


def get_power_consumption(date):
    date = str(date)
    url = "{}/farms/1699672/power_report".format(uri)
    payload = {
        "date": date,
        "period": "1d",
        "action": "download"
    }
    headers = {
        "Content-Type": contype,
        'Authorization': token
    }
    response = requests.request("GET", url, headers=headers, params=payload)
    if response.status_code == 200:
        dirname = os.path.dirname(__file__)
        # windows \\ linux /
        filename = os.path.join(dirname, 'PDF\\metadata.pdf')
        with open(filename, 'wb') as f:
            f.write(response.content)
            f.close
        temp = open(filename, 'rb')
        print(temp)
        pdf = PyPDF2.PdfFileReader(temp)
        first_page = pdf.getPage(0)
        text = first_page.extractText()
        split1 = text.split("ion: ")
        split2 = split1[1].split("Y")
        temp.close
        return split2[0]
    else:
        return -1


def test():
    url = "https://api2.hiveos.farm/api/v2/farms/1699672/metrics"
    payload = {}
    headers = {
        "Content-Type": contype,
        'Authorization': token
    }
    response = requests.request("GET", url, headers=headers, params=payload)
    return json.loads(response.text)

def get_hashrates():
    #get workers
    url = "{}/farms/1699672/stats".format(uri)
    payload = {}
    headers = {
        "Content-Type": contype,
        'Authorization': token
    }
    response = requests.request("GET", url, headers=headers, params=payload)
    return json.loads(response.text)["hashrates"]
    
def get_farm_stats():
    #get workers
    url = "{}/farms/1699672/stats".format(uri)
    payload = {}
    headers = {
        "Content-Type": contype,
        'Authorization': token
    }
    response = requests.request("GET", url, headers=headers, params=payload)
    return json.loads(response.text)["stats"]
  
