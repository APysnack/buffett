import sys
sys.path.append('C:/Users/purle/OneDrive/Desktop/buffett/objects')
import yfinance as yf
import datetime
from objects.stock import Stock
from objects.agent import Agent
from objects.state import State
from objects.actions import Actions

from extra.individual import individualReport
from pandas.tseries.holiday import USFederalHolidayCalendar
import concurrent.futures

tickerList = ["VOO", "AAPL"]
cal = USFederalHolidayCalendar()
holidays = cal.holidays(start='2000-01-01', end='2021-12-31').to_pydatetime()
stockList = []
dateList = []
threads = []

# finds the next date from the original date that is not a federal holiday or weekend


def extendDate(originalDate):
    while(originalDate.weekday() == 5 or originalDate.weekday() == 6 or (originalDate in holidays)):
        originalDate = (originalDate + datetime.timedelta(days=1))

    return originalDate


def getDateSequence(originalDate):
    while(originalDate.weekday() == 5 or originalDate.weekday() == 6 or (originalDate in holidays)):
        originalDate = (originalDate + datetime.timedelta(days=1))

    back_2d = (originalDate + datetime.timedelta(days=1))
    while(back_2d.weekday() == 5 or back_2d.weekday() == 6 or (back_2d in holidays)):
        back_2d = (back_2d + datetime.timedelta(days=1))

    back_1d = (back_2d + datetime.timedelta(days=1))
    while(back_1d.weekday() == 5 or back_1d.weekday() == 6 or (back_1d in holidays)):
        back_1d = (back_1d + datetime.timedelta(days=1))

    today = (back_1d + datetime.timedelta(days=1))
    while(today.weekday() == 5 or today.weekday() == 6 or (today in holidays)):
        today = (today + datetime.timedelta(days=1))

    return originalDate, back_2d, back_1d, today

# gets a list of dates that we're interested in for this analysis


def getDates(start_date):
    back_5y = datetime.datetime.strptime(start_date, "%m/%d/%y")
    back_5y = extendDate(back_5y)
    back_1y = (back_5y + datetime.timedelta(days=365 * 4))
    back_1y = extendDate(back_1y)
    back_9m = (back_5y + datetime.timedelta(days=365 * 5 - 270))
    back_9m = extendDate(back_9m)
    back_6m = (back_5y + datetime.timedelta(days=365 * 5 - 180))
    back_6m = extendDate(back_6m)
    back_3m = (back_5y + datetime.timedelta(days=365 * 5 - 90))
    back_3m = extendDate(back_3m)
    back_1m = (back_5y + datetime.timedelta(days=365 * 5 - 30))
    back_1m = extendDate(back_1m)
    back_1w = (back_5y + datetime.timedelta(days=365 * 5 - 7))
    back_1w = extendDate(back_1w)
    back_3d = (back_5y + datetime.timedelta(days=365 * 5 - 4))
    back_3d, back_2d, back_1d, today = getDateSequence(back_3d)

    dateList.extend([back_5y, back_1y, back_9m, back_6m, back_3m,
                    back_1m, back_1w, back_3d, back_2d, back_1d, today])

    return dateList


# for each stock ticker in the list of ticker, sets all the historic price data
# for that stock in the Stock object, implements threading
def setData():
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


def stockAnalysis():
    start_date = "05/28/14"

    # gets a list of dates to check values for 5 years back, 1, year, etc.
    # filters out weekends/US holidays
    dateList = getDates(start_date)
    today = dateList[-1].strftime('%m/%d/%y')

    # sets all the historic values on each Stock object in the stocklist
    setData()

    # calculates features such as risk, expected returns, etc. based on historic data
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(setStocks, stock) for stock in stockList]


if __name__ == "__main__":
    # val = int(input("Options:\n1. Indiviudal Stock Report\n2. Stock Analysis\n"))
    # if(val == 1):
    #     individualReport()
    # else:
    stockAnalysis()

    # initializes agent with name, starting cash
    buffett = Agent("buffett", 2000, stockList)
    buffett.assessActions()
    # buffet looks at all potential actions (buy/sell/hold for stocks in stock list)
    buffett.reportState()
