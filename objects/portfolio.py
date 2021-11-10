import math


class Portfolio:
    def __init__(self):
        self.stockList = []
        self.totalValue = 0
        self.aggregateRisk = 0

    def addStockToPortfolio(self, stock, numShares):
        self.totalValue += stock.price * numShares
        temp_dict = {
            "stockObj": stock,
            "shares": numShares,
            "percentage": 0
        }
        self.stockList.append(temp_dict)
        self.updateDiversity()

    def removeStockFromPortfolio(self, indexToSell, numShares):
        self.totalValue -= self.stockList[indexToSell]["stockObj"].price * numShares
        if (self.stockList[indexToSell]["shares"] - numShares) == 0:
            del self.stockList[indexToSell]
        elif (self.stockList[indexToSell]["shares"] - numShares) < 0:
            print("Error: trying to sell more stocks than what is owned")
        else:
            self.stockList[indexToSell]["shares"] = self.stockList[indexToSell]["shares"] - numShares
        self.updateDiversity()

    def getPortfolioSize(self):
        portSize = len(self.stockList)
        return portSize

    def getStockByIndex(self, index):
        return self.stockList[index]["stockObj"]

    def updateDiversity(self):
        self.aggregateRisk = 0
        for dictObj in self.stockList:
            percentOfPortfolio = (dictObj["stockObj"].price *
                                  dictObj["shares"]) / self.totalValue
            dictObj["percentage"] = percentOfPortfolio
            self.aggregateRisk += (percentOfPortfolio *
                                   dictObj["stockObj"].risk)

        # lowers risk based on number of stocks owned with diminishing returns
        stockVariety = len(self.stockList) + 1
        if(stockVariety <= 1):
            self.aggregateRisk = 0
        else:
            denom = math.log2(stockVariety)
            self.aggregateRisk = self.aggregateRisk / denom

        print(f'Collective risk of this portfolio is {self.aggregateRisk}')

    def __str__(self):
        output = 'Aggregate Risk: ' + str(self.aggregateRisk)
        output += ', Stocks Owned:'
        for stock in self.stockList:
            output += "[ "
            output += "name: " + stock["stockObj"].tickerName + ","
            output += " boughtPrice: " + str(stock["stockObj"].price) + ","
            output += " shares: " + str(stock["shares"]) + ","
            output += " expReturnPerShare: " + \
                str(stock["stockObj"].expectedReturn)
            output += "]"
        return output
