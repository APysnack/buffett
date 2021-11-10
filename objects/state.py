from objects.portfolio import Portfolio


class State:
    def __init__(self, cash):
        self.cash = cash
        self.totalExpectedReturn = 0
        self.cumulativeRisk = 0
        self.portfolio = Portfolio()

    def __str__(self):
        output = "[Cash: {}], [Expected Return: {}], ".format(
            self.cash, self.totalExpectedReturn)
        output = output + str(self.portfolio)
        return output

    def buy(self, stock, numShares):
        print(f'buying {numShares} shares of {stock.tickerName}')
        cost = stock.price * numShares
        self.cash = self.cash - cost
        self.totalExpectedReturn = self.totalExpectedReturn + \
            (stock.expectedReturn * numShares)
        self.cumulativeRisk = self.cumulativeRisk + (stock.risk * numShares)
        self.portfolio.addStockToPortfolio(stock, numShares)

    def sell(self, indexToSell, numShares, sellPrice):
        stock = self.portfolio.getStockByIndex(indexToSell)
        print(f'selling {numShares} shares of {stock.tickerName}')
        self.cash = self.cash + (numShares * sellPrice)
        self.totalExpectedReturn = self.totalExpectedReturn - \
            (stock.expectedReturn * numShares)
        self.cumulativeRisk = self.cumulativeRisk - (stock.risk * numShares)
        self.portfolio.removeStockFromPortfolio(indexToSell, numShares)
