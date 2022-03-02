import json
import time
import binanceapi
import datetime
import spreadsheet
from binance.client import Client
import os
import sys
import hiveapi
import pooldata

#Constants
original_stdout = sys.stdout # Save a reference to the original standard output
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'Json/config.json')
config = json.load(open(filename))
client = Client(config["api"], config["secret"])
root = os.path.abspath(os.curdir)
logfile = root + '\\Logs\\log.txt'
outputfile = root + '\\Logs\\output.txt'

def write_to_log(parameter):
  with open(logfile, 'a') as f:
    f.write(parameter)
    f.write('\n')
  f.close()

def update_power():
  #update power consumption
  today = datetime.date.today()
  yesterday = today - datetime.timedelta(days=1)
  power_consumption = hiveapi.get_power_consumption(str(yesterday))
  power_consumption = float(power_consumption) / 12000
  date_to_find = yesterday.strftime("%d-%b-%y")
  if (spreadsheet.find(date_to_find,6) != "false"):
    array = spreadsheet.find(date_to_find,6)
    positiontowrite = "B"+ str(array[0])
    spreadsheet.update(positiontowrite,power_consumption,6)
    write_to_log("Wrote {:.2f} to cell {}".format(power_consumption,positiontowrite))

def clear():
  if os.name == 'nt':
      _ = os.system('cls')
  else:
      _ = os.system('clear')

def update_deposits():
  #Get Deposits
  deposits = binanceapi.get_binance_pay_history()
  deposits_assets = deposits["data"]
  deposits_assets.reverse()
  for i in deposits_assets:
    date_time = datetime.datetime.strptime(time.ctime(i["transactionTime"]/1000), '%a %b %d %H:%M:%S %Y').strftime('%d/%m/%Y %H:%M:%S')
    if spreadsheet.find(date_time,8) == "false": #nothing found, determine where to write
      columns = spreadsheet.readcolumn(1,8)
      #write date
      positiontowrite = "A"+str(len(columns)+1)
      spreadsheet.update(positiontowrite,date_time,8)
      write_to_log("Wrote deposit date {} to cell {}".format(date_time,positiontowrite))
      deposit_currency = i["currency"]
      deposit_amount = float(i["amount"])
      #write crypto amount
      positiontowrite = "B"+str(len(columns)+1)
      spreadsheet.update(positiontowrite,str(deposit_amount) + " in " + str(deposit_currency),8)
      #determine price in EUR at time of deposit
      start = i["transactionTime"]
      if deposit_currency == "USDT":
        valueUSDTBTC=client.get_historical_klines("BTCUSDT",client.KLINE_INTERVAL_1MINUTE,start,start+60000,limit=1)
        valueBTCEUR=client.get_historical_klines("BTCEUR",client.KLINE_INTERVAL_1MINUTE,start,start+60000,limit=1)
        conversion1 = deposit_amount * 1/(float((float(valueUSDTBTC[0][2]) + float(valueUSDTBTC[0][3]))/2))
        deposit_value = conversion1 * float((float(valueBTCEUR[0][2]) + float(valueBTCEUR[0][3]))/2)
        positiontowrite = "C"+str(len(columns)+1)
        spreadsheet.update(positiontowrite,deposit_value,8)
        write_to_log("Wrote deposit value {:.2f} to cell {}".format(deposit_value,positiontowrite))
        continue
      sym = deposit_currency+"EUR"
      value=client.get_historical_klines(sym,client.KLINE_INTERVAL_1MINUTE,start,start+60000,limit=1)
      deposit_value = deposit_amount * (float(value[0][2]) + float(value[0][3]))/2
      positiontowrite = "C"+str(len(columns)+1)
      spreadsheet.update(positiontowrite,deposit_value,8)
      write_to_log("Wrote deposit value {:.2f} to cell {}".format(deposit_value,positiontowrite))

def update_balances():
  #Get account info
  account_info = client.get_account()
  account_balances = account_info['balances']
  totalinEur = 0.00
  for i in account_balances:
    if float(i["free"]) == 0.00 and float(i["locked"]) == 0.00 :
      continue
    else:
      #non-zero asset, lets determine the asset
      assetname = str(i["asset"])
      #asset balance
      assetbalance = float(i["free"]) + float(i["locked"])
      if assetname.startswith("LD"):
        assetname = assetname.lstrip('LD')
      #check its not usdt
      if assetname == "USDT":
        valueUSDTBTC=client.get_avg_price(symbol="BTCUSDT")
        valueBTCEUR=client.get_avg_price(symbol="BTCEUR")
        conversion1 = assetbalance * (1/float(valueUSDTBTC["price"]))
        totalinEur += float(conversion1 * float(valueBTCEUR["price"]))
        continue
      #we have asset, lets get the value
      sym = str(assetname)+"EUR"
      value=client.get_avg_price(symbol=sym)
      totalinEur += assetbalance * float(value["price"])
  now = datetime.datetime.now()
  start = now.strftime("%d/%m/%Y %H:%M:%S")
  if spreadsheet.find(start,8) == "false": #nothing found, determine where to write
      columns = spreadsheet.readcolumn(7,8)
      #write date
      positiontowrite = "G"+str(len(columns)+1)
      spreadsheet.update(positiontowrite,start,8)
      positiontowrite = "H"+str(len(columns)+1)
      spreadsheet.update(positiontowrite,totalinEur,8)
      write_to_log("Wrote total balance {:.2f} to cell {}".format(totalinEur,positiontowrite))

def update_coin_prices():
    #update ETH price
    sym = "ETHEUR"
    ethprice=client.get_avg_price(symbol=sym)
    ethtoeur = float(ethprice["price"])
    positiontowrite = "N9"
    spreadsheet.update(positiontowrite,ethtoeur,8)
    write_to_log("Wrote eth price {:.2f} to cell {}".format(ethtoeur,positiontowrite))
    #update BNB price
    sym = "BNBEUR"
    bnbprice=client.get_avg_price(symbol=sym)
    bnbtoeur = float(bnbprice["price"])
    positiontowrite = "O9"
    spreadsheet.update(positiontowrite,bnbtoeur,8)
    write_to_log("Wrote BNB price {:.2f} to cell {}".format(bnbtoeur,positiontowrite))

def update_pool_data():
  #Adjusted to only 1 pool
  #find where to write
  columns = spreadsheet.readcolumn(4,7)
  #establish positions
  positionrig2 = "F"+str(len(columns)+1)
  positiondatetime = "D"+str(len(columns)+1)
  deltarig2 = float(pooldata.flexpool())
  now = datetime.datetime.now()
  start = now.strftime("%d/%m/%Y %H:%M:%S")
  #write
  spreadsheet.update(positionrig2,deltarig2,7)
  write_to_log("Wrote rig pool balance {:.2f} to cell {}".format(deltarig2,positionrig2))
  spreadsheet.update(positiondatetime,start,7)
  write_to_log("Wrote pool data update time {} to cell {}".format(start,positiondatetime))

def writeupdatetofile(param):
  if param == False:
    file = open(outputfile, 'w')
    file.truncate(0)
    file.write("Update in progress...")
    file.close()
  elif param == True:
    file = open(logfile, 'r')
    file2 = open(outputfile, 'w')
    for line in file:
      file2.write(line)
    file2.close()
    file.close()

def mainloop():
  while True:
    with open(logfile, 'w') as f:
      f.truncate(0)
      f.close()
    writeupdatetofile(False)
    update_power()
    update_balances()
    update_deposits()
    update_pool_data()
    update_coin_prices()
    now = datetime.datetime.now()
    then = now + datetime.timedelta(hours=6)
    timenow = now.strftime("%d/%m/%Y %H:%M:%S")
    timethen = then.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    write_to_log("Going to sleep at {}".format(timenow))
    write_to_log("Next update at {}".format(timethen))
    writeupdatetofile(True)
    wasted = 0
    for i in range(7200):
        print("Waited for {}...".format(i))
        wasted = wasted + 1
        now = datetime.datetime.now()
        time.sleep(30)
