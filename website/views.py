from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
import si_prefix
import hiveapi
import spreadsheet
import datetime
import os

# Constants
views = Blueprint('views', __name__)
lastupdate = datetime.datetime.now() + datetime.timedelta(days=-1)
lastupdate1 = datetime.datetime.now() + datetime.timedelta(days=-1)
lastupdate2 = datetime.datetime.now() + datetime.timedelta(days=-1)
# windows \\ linux /
root = os.path.abspath(os.curdir)
hashlog = root + "\\Logs\\hashdata.txt"
workerlog = root + "\\Logs\\workerdata.txt"
moneylog = root + "\\Logs\\moneydata.txt" 
outputlog = root + "\\Logs\\output.txt"
files = [hashlog,workerlog,moneylog]

def create_files(param):
    for file in param:
        with open(file, 'w') as f:
            f.close
            

def hashrate_data():
    hash_data = []
    global hashlog
    now = datetime.datetime.now()
    global lastupdate1
    if now - lastupdate1 > datetime.timedelta(minutes=2):
        try:
            hash_data_raw = hiveapi.get_hashrates()
            for item in hash_data_raw:
                algostring = item.get("algo").capitalize()
                multiplier = 1000
                algohash = si_prefix.si_format(
                    item.get("hashrate") * multiplier, 3)
                hash_data.append(algostring + ' : ' + algohash + 'H/s')
            with open(hashlog, "w") as f:
                for line in hash_data:
                    f.write(line)
                    f.write('\n')
                f.close
            lastupdate1 = now
            return hash_data
        except Exception:
            with open(hashlog, "r") as f:
                for line in f.readlines():
                    hash_data.append(line)
                f.close
            return hash_data
    else:
        with open(hashlog, "r") as f:
            for line in f.readlines():
                hash_data.append(line)
            f.close
        return hash_data


def get_worker_data():
    global workerlog
    worker_data = []
    now = datetime.datetime.now()
    global lastupdate2
    if now - lastupdate2 > datetime.timedelta(minutes=5):
        try:
            worker_data_raw = hiveapi.get_farm_stats()
            worker_data.append("Total rigs : " +
                               str(worker_data_raw.get("workers_total")))
            worker_data.append("Active rigs : " +
                               str(worker_data_raw.get("workers_online")))
            worker_data.append("Total GPUS : " +
                               str(worker_data_raw.get("gpus_total")))
            worker_data.append("Active GPUS : " +
                               str(worker_data_raw.get("gpus_online")))
            worker_data.append(
                "Current power draw : " + si_prefix.si_format(worker_data_raw.get("power_draw"), 3) + "W")
            with open(workerlog, "w") as f:
                for line in worker_data:
                    f.write(line)
                    f.write('\n')
                f.close
            lastupdate2 = now
            return worker_data
        except Exception:
            with open(workerlog, "r") as f:
                for line in f.readlines():
                    worker_data.append(line)
                f.close
            return worker_data
    else:
        with open(workerlog, "r") as f:
            for line in f.readlines():
                worker_data.append(line)
            f.close
        return worker_data


def get_money_data():
    global moneylog
    money_data = []
    now = datetime.datetime.now()
    global lastupdate
    if now - lastupdate > datetime.timedelta(hours=1):
        try:
            money_data.append(
                "Total deposited - Value at date of deposit: " + str(spreadsheet.cellvalue(2, 11, 8)))
            money_data.append("Gain/Loss from fluctuations : " +
                              str(spreadsheet.cellvalue(2, 12, 8)))
            money_data.append("Total in crypto : " +
                              str(spreadsheet.cellvalue(2, 13, 8)) + " ETH")
            money_data.append(
                "Total : " + str(spreadsheet.cellvalue(6, 10, 8)))
            money_data.append("Electricity costs : " +
                              str(spreadsheet.cellvalue(6, 11, 8)))
            money_data.append(
                "Revenue : " + str(spreadsheet.cellvalue(6, 12, 8)))
            money_data.append(
                "ROI : " + str(spreadsheet.cellvalue(6, 13, 8)) + "%")
            money_data.append(
                "ROI ETA: " + str(spreadsheet.cellvalue(9, 13, 8)) + " days")
            with open(moneylog, "w") as f:
                for line in money_data:
                    f.write(line)
                    f.write('\n')
                f.close
            lastupdate = now
            return money_data
        except Exception:
            with open(moneylog, "r") as f:
                for line in f.readlines():
                    money_data.append(line)
                f.close
            return money_data
    else:
        with open(moneylog, "r") as f:
            for line in f.readlines():
                money_data.append(line)
            f.close
        return money_data


def get_backend_output():
    data_out = []
    global outputlog
    try:
        with open(outputlog, 'r') as text:
            reader = text.readlines()
            for line in reader:
                data_out.append(line)
        text.close()
        return data_out
    except Exception:
        return data_out

#Load
create_files(files)
hash_data = hashrate_data()
worker_data = get_worker_data()
money_data = get_money_data()

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # load data
    hash_data = hashrate_data()
    worker_data = get_worker_data()
    money_data = get_money_data()
    # load output of backend.py
    data_out = get_backend_output()
    date = " "
    # load next update
    if not data_out:
        print("nodata")
    if data_out:
        lastentry = data_out[-1]
        date = lastentry.split("Next update at ")
    if len(date) >= 2:
        date = date[1].split("\n")
        data_out.pop(-1)
        return render_template("home.html", user=current_user, data=data_out, hashdata=hash_data, workerdata=worker_data, moneydata=money_data, nextupdate=date[0])
    else:
        return render_template("home.html", user=current_user, data=data_out, hashdata=hash_data, workerdata=worker_data, moneydata=money_data, nextupdate="01 Jan 2000 00:00:01")
