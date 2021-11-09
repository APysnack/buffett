import sys
sys.path.append('C:/Users/purle/OneDrive/Desktop/buffett/objects')
import yfinance as yf
from utils.utils import *
from objects.stock import Stock
from objects.agent import Agent
from objects.state import State
from objects.actions import Actions

tickerList = ["VOO", "AAPL", "AMZN", "NFLX", "ROST", "NVDA"]

if __name__ == "__main__":
    # val = int(input("Options:\n1. Individual Stock Report\n2. Stock Analysis\n"))
    # if(val == 1):
    #     individualReport()
    # else:
    stockAnalysis(tickerList)

    # initializes agent with name, starting cash, list of stock data
    buffett = Agent("buffett", 2000, stockList)

    # buffet looks at all potential actions (buy/sell/hold for stocks in stock list)
    buffett.assessActions()

    # report decision
    buffett.reportState()

    apple = Stock()
    apple.tickerName = 'AAPL'
    apple.price = 50

    buffett.sellAll(apple)
    buffett.reportState()
