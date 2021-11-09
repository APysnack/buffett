class Portfolio:
    def __init__(self):
        self.stockList = []

    def addStockToPortfolio(self, stock):
        self.stockList.append(stock)

    def removeStockFromPortfolio(self, stock):
        try:
            self.stockList.remove(stock)
        except ValueError:
            print("item not in list")

    def __str__(self):
        output = '[Stocks Owned:'
        for stock in self.stockList:
            output += f" {stock.tickerName}, "
        output += ']'
        return output
