from pandas.tseries import offsets
import yfinance as yf
import datetime
from pandas.tseries.holiday import USFederalHolidayCalendar
import concurrent.futures
import numpy as np
import pandas as pd
from pandas_datareader import data as web
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import mplfinance as mpf
import time
import csv
import os

cal = USFederalHolidayCalendar()
holidays = cal.holidays(start='2000-01-01', end='2021-12-31').to_pydatetime()
stockList = []
dateList = []
threads = []
stocksNotDownloaded = []


# for each stock ticker in the list of ticker, sets all the historic price data
# for that stock in the Stock object, implements threading
def setData(tickerList):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(getData, ticker) for ticker in tickerList]


# gets historic data for the stock ticker indicated on the dates in the date list
def getData(ticker):
    stock = Stock()
    tick = yf.Ticker(ticker)
    stock.setTickerName(ticker)

    for i, date in enumerate(dateList):
        end_date = (date + datetime.timedelta(days=1))
        end_date = extendDate(end_date)
        try:
            hist = tick.history(start=date.date(), end=end_date.date())
            if 'Empty DataFrame' in str(hist):
                raise Exception(
                    'Empty DataFrame - might be caused by an invalid symbol')

            else:
                high = hist.iloc[0]["High"]
                low = hist.iloc[0]["Low"]

        except Exception as e:
            high = 0
            low = 0

        stock.setDateValues(i, high, low)

    stockList.append(stock)


def setStocks(stock):
    stock.setRisk()
    stock.set_Z_Score()
    stock.set_momentum()


def stockAnalysis(tickerList):
    start_date = "05/28/14"
    # gets a list of dates to check values for 5 years back, 1, year, etc.
    # filters out weekends/US holidays
    dateList = getDates(start_date)
    today = dateList[-1].strftime('%m/%d/%y')

    # sets all the historic values on each Stock object in the stocklist
    setData(tickerList)

    # calculates features such as risk, expected returns, etc. based on historic data
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(setStocks, stock) for stock in stockList]


def save_to_csv_from_yahoo(folder, ticker, syear, smonth, sday, eyear, emonth, eday):
    start = dt.datetime(syear, smonth, sday)
    end = dt.datetime(eyear, emonth, eday)
    print(start)
    try:
        df = web.DataReader(ticker, 'yahoo', start, end)
        time.sleep(10)
        df.to_csv(folder + ticker + '.csv')
    except Exception:
        print(f'Error downloading {ticker}')
        stocksNotDownloaded.append(ticker)


def get_column_from_csv(file, col_name):
    try:
        df = pd.read_csv(file)
    except FileNotFoundError:
        print(f'File {file} does not exist')
    else:
        return df[col_name]


def get_df_from_csv(folder, ticker):
    try:
        df = pd.read_csv(folder + ticker + '.csv')
    except FileNotFoundError:
        print(f"File for {ticker} does not exist")
    else:
        return df


def save_df_to_csv(df, folder, ticker):
    try:
        df.to_csv(folder + ticker + '.csv')
    except Exception:
        print(f"Error saving df for {ticker} to csv")


def save_df_to_csv_without_index(df, folder, ticker):
    try:
        df.to_csv(folder + ticker + '.csv', index=False)
    except Exception:
        print(f"Error saving df for {ticker} to csv")


def delete_unnamed_cols(df):
    try:
        df.drop(df.columns[df.columns.str.contains('unnamed', case=False)],
                axis=1, inplace=True)
    except Exception:
        pass
    return df


def add_daily_return_to_df(df, folder, ticker, title, offset):
    df[title] = (df['Adj Close'].shift(offset) / df['Adj Close']) - 1
    df.to_csv(folder + ticker + '.csv')
    return df


def add_momentum_to_df(df, folder, ticker):
    df['1d_momentum'] = (df['z_score'] - df['yesterday_z'])
    df['2d_momentum'] = (df['z_score'] - df['2_days_back_z'])
    df['3d_momentum'] = (df['z_score'] - df['3_days_back_z'])
    df.to_csv(folder + ticker + '.csv')
    return df


def add_z_score_to_df(df, folder, ticker):
    mean = df['Adj Close'].mean()
    sd = df['Adj Close'].std()
    df['z_score'] = (df['Adj Close'] - mean) / sd
    df.to_csv(folder + ticker + '.csv')
    return df


def add_prev_z_to_df(df, folder, ticker, title, parent_title, offset):
    try:
        df[title] = df[parent_title].shift(offset)
        df.to_csv(folder + ticker + '.csv')
    except Exception:
        pass
    return df


def add_col_to_df(df, folder, ticker, col_name, item_to_add):
    df[col_name] = item_to_add
    df.to_csv(folder + ticker + '.csv')


def get_roi_between_dates(df, sdate, edate):
    try:
        df = df.set_index(['Date'])
        start_val = df.loc[sdate, 'Adj Close']
        end_val = df.loc[edate, 'Adj Close']
        roi = (end_val - start_val) / start_val
    except Exception:
        print('get ROI failed')
    else:
        return roi


def get_mean_between_dates(df, sdate, edate):
    mask = (df['Date'] >= sdate) & (df['Date'] <= edate)
    return df.loc[mask]['Adj Close'].mean()


def get_std_between_dates(df, sdate, edate):
    mask = (df['Date'] >= sdate) & (df['Date'] <= edate)
    return df.loc[mask]['Adj Close'].std()


def get_cov_between_dates(df, sdate, edate):
    mean = get_mean_between_dates(df, sdate, edate)
    std = get_std_between_dates(df, sdate, edate)
    return std / mean


def format_date_str(sdate, edate):
    sdate = '-'.join(('0' if len(x) < 2 else '') +
                     x for x in sdate.split('-'))
    edate = '-'.join(('0' if len(x) < 2 else '') +
                     x for x in edate.split('-'))

    return sdate, edate


def get_cov_roi(tickers, folder, sdate, edate):
    col_names = ["Ticker", "COV", "ROI"]
    df = pd.DataFrame(columns=col_names)
    for ticker in tickers:
        print("Working on: ", ticker)
        s_df = get_df_from_csv(folder, ticker)
        sdate, edate = get_valid_dates(s_df, sdate, edate)
        cov = get_cov_between_dates(s_df, sdate, edate)
        s_df = s_df.set_index(['Date'])
        roi = get_roi_between_dates(s_df, sdate, edate)
        df.loc[len(df.index)] = [ticker, cov, roi]
    return df


def merge_df_by_col_name(col_name, folder, sdate, edate, *tickers):
    mult_df = pd.DataFrame()
    for ticker in tickers:
        df = get_df_from_csv(folder, ticker)
        df['Date'] = pd.to_datetime(df['Date'])
        mask = (df['Date'] >= sdate) & (df['Date'] <= edate)
        mult_df[ticker] = df.loc[mask][col_name]
    return mult_df


def get_valid_dates(df, sdate, edate):
    try:
        mask = (df['Date'] >= sdate) & (df['Date'] <= edate)
        sm_df = df.loc[mask]
        sm_df = sm_df.set_index(['Date'])
        first_date = sm_df.index.min()
        last_date = sm_df.index.max()
        date_leading, date_ending = format_date_str(first_date, last_date)
        return date_leading, date_ending
    except Exception:
        print("Date data is corrupted")


def csv_to_arff(in_file, out_file, title):
    fileToRead = in_file
    fileToWrite = out_file
    relation = title

    dataType = []  # Stores data types 'nominal' and 'numeric'
    columnsTemp = []  # Temporary stores each column of csv file except the attributes
    uniqueTemp = []  # Temporary Stores each data cell unique of each column
    uniqueOfColumn = []  # Stores each data cell unique of each column
    dataTypeTemp = []  # Temporary stores the data type for cells on each column
    finalDataType = []  # Finally stores data types 'nominal' and 'numeric'
    attTypes = []  # Stores data type 'numeric' and nominal data for attributes
    p = 0  # pointer for each cell of csv file

    writeFile = open(fileToWrite, 'w')

    # Opening and Reading a CSV file
    f = open(fileToRead, 'r')
    reader = csv.reader(f)
    allData = list(reader)
    attributes = allData[0]
    totalCols = len(attributes)
    totalRows = len(allData)
    f.close()

    # Add a '0' for each empty cell
    for j in range(0, totalCols):
        for i in range(0, totalRows):
            if 0 == len(allData[i][j]):
                allData[i][j] = "0"

    # check for comams or blanks and adds single quotes
    for j in range(0, totalCols):
        for i in range(1, totalRows):
            allData[i][j] = allData[i][j].lower()
            if "\r" in allData[i][j] or '\r' in allData[i][j] or "\n" in allData[i][j] or '\n' in allData[i][j]:
                allData[i][j] = allData[i][j].rstrip(os.linesep)
                allData[i][j] = allData[i][j].rstrip("\n")
                allData[i][j] = allData[i][j].rstrip("\r")
            try:
                if allData[i][j] == str(float(allData[i][j])) or allData[i][j] == str(int(allData[i][j])):
                    print
            except ValueError as e:
                allData[i][j] = "'" + allData[i][j] + "'"

    # fin gives unique cells for nominal and numeric
    for j in range(0, totalCols):
        for i in range(1, totalRows):
            columnsTemp.append(allData[i][j])
        for item in columnsTemp:
            if not (item in uniqueTemp):
                uniqueTemp.append(item)
        uniqueOfColumn.append("{" + ','.join(uniqueTemp) + "}")
        uniqueTemp = []
        columnsTemp = []

    # Assigns numeric or nominal to each cell
    for j in range(1, totalRows):
        for i in range(0, totalCols):
            try:
                if allData[j][i] == str(float(allData[j][i])) or allData[j][i] == str(int(allData[j][i])):
                    dataType.append("numeric")
            except ValueError as e:
                dataType.append("nominal")

    for j in range(0, totalCols):
        p = j
        for i in range(0, (totalRows - 1)):
            dataTypeTemp.append(dataType[p])
            p += totalCols
        if "nominal" in dataTypeTemp:
            finalDataType .append("nominal")
        else:
            finalDataType .append("numeric")
        dataTypeTemp = []

    for i in range(0, len(finalDataType)):
        if finalDataType[i] == "nominal":
            attTypes.append(uniqueOfColumn[i])
        else:
            attTypes.append(finalDataType[i])

    # Show comments
    writeFile.write("%\n% Comments go after a '%' sign.\n%\n")
    writeFile.write("%\n% Relation: " + relation + "\n%\n%\n")
    writeFile.write("% Attributes: " + str(totalCols) + " " * 5
                    + "Instances: " + str(totalRows - 1) + "\n%\n%\n\n")

    # Show Relation
    writeFile.write("@relation " + relation + "\n\n")

    # Show Attributes
    for i in range(0, totalCols):
        writeFile.write("@attribute" + " '" + attributes[i]
                        + "' " + attTypes[i] + "\n")

    # Show Data
    writeFile.write("\n@data\n")
    for i in range(1, totalRows):
        writeFile.write(','.join(allData[i]) + "\n")

    print(fileToWrite + " was converted to " + fileToRead)
