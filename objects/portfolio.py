class Portfolio:
    def __init__(self):
        self.stockList = []

    def addStockToPortfolio(self, stock, numShares):
        temp_dict = {
            "stockObj": stock,
            "shares": numShares,
        }

        self.stockList.append(temp_dict)

    def removeStockFromPortfolio(self, indexToSell, numShares):
        if (numShares - self.stockList[indexToSell]["shares"]) == 0:
            del self.stockList[indexToSell]
        elif (numShares - self.stockList[indexToSell]["shares"]) < 0:
            print("Error: trying to sell more stocks than what is owned")
        else:
            self.stockList[indexToSell]["shares"] = self.stockList[indexToSell["shares"]] - numShares

    def getPortfolioSize(self):
        portSize = len(self.stockList)
        return portSize

    def getStockByIndex(self, index):
        return self.stockList[index]["stockObj"]

    def __str__(self):
        output = 'Stocks Owned:'
        for stock in self.stockList:
            output += "[ "
            output += "name: " + stock["stockObj"].tickerName + ","
            output += " boughtPrice: " + str(stock["stockObj"].price) + ","
            output += " shares: " + str(stock["shares"]) + ","
            output += " expReturnPerShare: " + \
                str(stock["stockObj"].expectedReturn)
            output += "]"
        return output
