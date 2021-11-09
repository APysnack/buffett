import yfinance as yf
import math
import numpy as np


class Stock:
    def __init__(self):
        # primary object variables
        self.tickerName = None

        # speculative risk value
        self.risk = None

        # current price deviation
        # mean is calculated from only a few sampled points over the last year
        # large (positive) z-scores represent heavily sold entities
        self.z_score = None

        # today's average price
        self.price = None

        # short term momentum data
        # values > 1, risk goes down
        # values < 1, risk goes up
        self.week_to_day3_momentum = None
        self.day3_to_day2_momentum = None
        self.day3_to_day1_momentum = None
        self.day2_to_day1_momentum = None
        self.day1_to_day0_momentum = None

        # amount expected to be returned from investment
        self.expectedReturn = None

        # adjustable value for calculating the expected return from a stock
        # expectedReturn = (formula price * z_score) / variableRate
        self.variableRate = 20

    def setTickerName(self, tickerName):
        self.tickerName = tickerName
        self.tickerObj = yf.Ticker(self.tickerName)

    def setEmployees(self, numEmployees):
        self.employees = numEmployees

    def __str__(self):
        output = "[Name: {}], [5 year: {}], [1 year: {}], [9 month: {}], [6 month: {}], [3 month: {}], [1 month: {}], [1 week: {}], [Back_3d: {}], [Back_2d: {}], [Back_1d: {}], [today's price: {}], [Risk: {}], [Z-Score: {}], [Expected Return: {}]\n\n".format(
            self.tickerName, self.back_5y, self.back_1y, self.back_9m, self.back_6m, self.back_3m, self.back_1m, self.back_1w, self.back_3d_high, self.back_2d_high, self.yesterday_high, self.price, self.risk, self.z_score, self.expectedReturn)
        return output

    def setDateValues(self, index, high, low):
        if(index == 0):
            self.back_5y = (high + low) / 2

        elif(index == 1):
            self.back_1y = (high + low) / 2

        elif(index == 2):
            self.back_9m = (high + low) / 2

        elif(index == 3):
            self.back_6m = (high + low) / 2

        elif(index == 4):
            self.back_3m = (high + low) / 2

        elif(index == 5):
            self.back_1m = (high + low) / 2

        elif(index == 6):
            self.back_1w = (high + low) / 2

        elif(index == 7):
            self.back_3d_high = high
            self.back_3d_low = low
            self.back_3d_avg = (high + low) / 2

        elif(index == 8):
            self.back_2d_high = high
            self.back_2d_low = low
            self.back_2d_avg = (high + low) / 2

        elif(index == 9):
            self.yesterday_high = high
            self.yesterday_low = low
            self.yesterday_avg = (high + low) / 2
        else:
            self.today_high = high
            self.today_low = low
            self.today_avg = (high + low) / 2
            self.price = self.today_avg

    def setRisk(self):
        try:
            self.employees = self.tickerObj.info['fullTimeEmployees']
            self.emp_factor = math.log(self.employees) - 3
        except KeyError:
            self.emp_factor = 0

        try:
            self.type = self.tickerObj.info['quoteType']

        except KeyError:
            self.type = 'unknown'

        self.setExpectedRisk()

    def setExpectedRisk(self):

        if(self.type == 'EQUITY'):
            typeBonus = 0
        else:
            typeBonus = 1.5

        if(int(self.back_5y) > 0):
            long_term_gain = ((self.back_3m / self.back_5y) - 0.15)
        else:
            long_term_gain = 0.7

        if not (int(self.back_1y) > 0):
            long_term_gain = 0.5

        if not (int(self.back_6m) > 0):
            long_term_gain = 0.4

        if not (int(self.back_3m) > 0):
            long_term_gain = 0.3

        data = long_term_gain + (self.emp_factor / 10) + typeBonus

        # lower numbers are higher risk
        self.risk = self.normalize(data, 4, 0)

    def normalize(self, val, max, min):
        return (val - min) / (max - min)

    def getMean(self, numList, n):
        sum = 0
        for num in numList:
            sum += num
        mean = sum / n
        return mean

    def getStd(self, numList, n, mean):
        sum = 0
        for num in numList:
            sum += ((num - mean)**2)

        std = math.sqrt(sum / (n - 1))
        return std

    def set_momentum(self):
        self.week_to_day3_momentum = self.back_3d_avg / self.back_1w
        self.day3_to_day2_momentum = self.back_2d_avg / self.back_3d_avg
        self.day3_to_day1_momentum = self.yesterday_avg / self.back_3d_avg
        self.day2_to_day1_momentum = self.yesterday_avg / self.back_2d_avg
        self.day1_to_day0_momentum = self.today_avg / self.yesterday_avg

    def set_Z_Score(self):
        numList = []
        if(int(self.back_1y) > 0.5):
            numList.append(self.back_1y)
        if(int(self.back_9m) > 0.5):
            numList.append(self.back_9m)
        if(int(self.back_6m) > 0.5):
            numList.append(self.back_6m)
        if(int(self.back_3m) > 0.5):
            numList.append(self.back_3m)
        if(int(self.back_1m) > 0.5):
            numList.append(self.back_1m)
        if(int(self.back_1w > 0.5)):
            numList.append(self.back_1w)
        if(int(self.back_1w) > 0.5):
            numList.append(self.back_3d_high)
        if(int(self.back_3d_low) > 0.5):
            numList.append(self.back_3d_low)

        n = len(numList)

        if n > 1:
            self.mean = self.getMean(numList, n)
            self.std = self.getStd(numList, n, self.mean)
        else:
            self.mean = 0
            self.std = 0

        if(self.mean == 0 or self.std == 0):
            self.z_score = 0
            self.expectedReturn = 0
        else:
            self.z_score = (self.today_avg - self.mean) / self.std
            self.expectedReturn = (
                self.today_avg * self.z_score) / self.variableRate
