import sys
import os
import time
import requests
import json
import datetime

INCLUDED_FIELDS = ['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj_Open', 'Adj_High', 'Adj_Low', 'Adj_Close', 'Adj_Volume']
EODQ_PATH = "/home/sma-analytics/Data/Quandl_Price/EODQ_Update/"
DEF_RETURNS_FILE_PATH = "/home/sma-analytics/Data/Returns/returns_data.txt"
MASTER_FILE_PATH = "/home/sma-analytics/Data/Returns/master_data.txt"
API_URL = "https://api.socialmarketanalytics.com/api/search?"
API_KEY = "b558cc935cf166ae72d8cd734ac4a8c614cf7aec"
SPY_PATH = "/home/sma-analytics/Data/Quandl_Price/SPY.csv"


daily_tickers = {}

#Gets UTC date
def get_date():

    t = time.strftime("%Y-%m-%d")
    t = datetime.datetime.strptime(t, "%Y-%m-%d") - datetime.timedelta(days=1)
    t = t.strftime("%Y-%m-%d")

    return t


TODAYS_DATE = get_date()


#Fetch the SPY data from its file
def fetch_spy():

    spy_data = {}

    with open(SPY_PATH) as f:
        headers = f.readline().split(",")
        first_line = f.readline().split(",")

        for i in range(len(headers)):
            spy_data[headers[i]] = first_line[i]

        #compute return
        spy_data['return'] = float(spy_data['Adj_Close']) / float(spy_data['Adj_Open']) - 1

    return spy_data['return']


#Assume today is a trading day if AAPL was traded
def is_trading_day():
    #Check if today is a trading day
    with open(EODQ_PATH + "AAPL.txt") as f:
        f.readline()
        content = f.readline()
        todays_date = get_date()
        content = content.split("\t")

        if todays_date == content[0]:
            return True
        return False



def get_sma_data():
    e_string = ""
    ninetentime = e_string.join(TODAYS_DATE.split("-")) + '0910'
    fifteenfourtytime = e_string.join(TODAYS_DATE.split("-")) + '1540'
    #search parameters
    params = {'subject':'all',\
            'ontology':'ticker',\
            'items':'sscore',\
            'dates':'datetime ge ' + ninetentime,\
            'frequency':'1d',\
            'format':'json',\
            'timezone':'UTC',\
            'limit':9000}

    #api key and function specification
    data = {'function':'search',\
            'api_key':API_KEY}

    ntdata = requests.post(API_URL, data=data, params=params).content

    params['dates'] = 'datetime ge ' + fifteenfourtytime

    ffdata = requests.post(API_URL, data=data, params=params).content
    return (ntdata, ffdata)



def append_ticker(ticker_file_path):

    #Open Quandl file of corresponding ticker
    with open(EODQ_PATH + ticker_file_path) as f:

        todays_trading_day = {}
        prev_trading_day = {}
        todays_date = get_date()

        #first line is the headers
        headers = f.readline()[:-1].split('\t')

        #second line is most recent trading day
        content = f.readline()[:-1].split('\t')

        #Make data accessible by key/value pairs
        for i in range(len(headers)):
            todays_trading_day[headers[i]] = content[i]

        #Next most recent trading data
        content = f.readline()[:-1].split('\t')

        for i in range(len(headers)):
            prev_trading_day[headers[i]] = content[i]

        #Don't use the data if it's not from today
        if not todays_date == todays_trading_day['Date']:
            return 0

        #Maintain Price > 5 Universe
        if float(prev_trading_day['Close']) < 5:
            return 0

        #append the ticker to the global list
        daily_tickers[todays_trading_day['ticker']] = todays_trading_day

        #appended ticker successfully
        return 1

def append_sma_data(ntdata, ffdata):
    ntdata = json.loads(ntdata.decode())['response']['data']
    ffdata = json.loads(ffdata.decode())['response']['data']
    count = 0
    for row in ntdata:
        if row['subject'] in daily_tickers.keys():
            d = row['datetime'].split()
            if d[0] == TODAYS_DATE and d[1] == "14:10:00":
                count += 1
                daily_tickers[row['subject']]['09:10 S-Score'] = row['sscore']

    for row in ffdata:
        if row['subject'] in daily_tickers.keys():
            d = row['datetime'].split()
            if d[0] == TODAYS_DATE and d[1] == "20:40:00":
                daily_tickers[row['subject']]['15:40 S-Score'] = row['sscore']

def calc_default_returns():
    count = 0
    pos_count = 0
    neg_count = 0
    rsum = 0
    pos_rsum = 0
    neg_rsum = 0
    for key, val in daily_tickers.items():

        val['return'] = float(val['Adj_Close']) / float(val['Adj_Open']) - 1
        count += 1
        rsum += val['return']

        if '09:10 S-Score' in val.keys():
            if float(val['09:10 S-Score']) >= 2:
                pos_count += 1
                pos_rsum += val['return']

            elif float(val['09:10 S-Score']) <= -2:
                neg_count += 1
                neg_rsum += val['return']

    ret_data = []
    ret_data.append([TODAYS_DATE, "Short", neg_rsum/ neg_count])
    ret_data.append([TODAYS_DATE, "SPY", fetch_spy()])
    ret_data.append([TODAYS_DATE, "Long", pos_rsum / pos_count])
    ret_data.append([TODAYS_DATE, "LS", ret_data[2][2] - ret_data[0][2]])

    lines = [TODAYS_DATE]

    for row in ret_data:
        lines.append(str(row[2]))

    lines = "\t".join(lines) + "\n"

    with open(DEF_RETURNS_FILE_PATH, "a") as f:
        f.write(lines)

def store_full_data():
    try:
        with open(MASTER_FILE_PATH, "a") as f:
            headers = ["ticker", "date"]
            for key, val in daily_tickers.items():
                line []
                for k, v in val.items():
                    line.append(v)
                line = "\t".join(v) + "\n"
                f.write(line)
    except:
        print("failure storing full data")

def main():

    if not is_trading_day() is True:
        print("Today is not a trading day: " + TODAYS_DATE)
        return

    lines_count = 0

    for ticker_path in os.listdir(EODQ_PATH):
        lines_count += append_ticker(ticker_path)

    ntdata, ffdata = get_sma_data()

    append_sma_data(ntdata, ffdata)

    calc_default_returns()

    store_full_data()


main()
