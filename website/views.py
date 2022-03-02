from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
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

def read_file(parameter):
    data = []
    try:
        with open(parameter, 'r') as file:
            reader = file.readlines()
            for line in reader:
                data.append(line)
            file.close()
        return data
    except Exception:
        return data


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # load data
    global hashlog
    global workerlog
    global moneylog
    global outputlog
    hash_data = read_file(hashlog)
    worker_data = read_file(workerlog)
    money_data = read_file(moneylog)
    data_out = read_file(outputlog)
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
