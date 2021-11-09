from objects.portfolio import Portfolio


class State:
    def __init__(self, cash):
        self.cash = cash
        self.expectedReturn = 0
        self.cumulativeRisk = 0
        self.aggregateRisk = 0
        self.portfolio = Portfolio()

    def __str__(self):
        output = "[Cash: {}], [Expected Return: {}], [Aggregate Risk: {}], ".format(
            self.cash, self.expectedReturn, self.aggregateRisk)
        output = output + str(self.portfolio)
        return output

    def buy(self, stock, numShares):
        self.cash = self.cash - (stock.price * numShares)
        self.expectedReturn = self.expectedReturn + \
            (stock.expectedReturn * numShares)
        self.cumulativeRisk = self.cumulativeRisk + (stock.risk * numShares)
        self.portfolio.addStockToPortfolio(stock, numShares)

    def sell(self, indexToSell, numShares):
        stock = self.portfolio.getStockByIndex(indexToSell)
        # FOO currently hardcoded. needs to get new stock data at the time of sale
        self.cash = 2000
        self.expectedReturn = self.expectedReturn - \
            (stock.expectedReturn * numShares)
        self.cumulativeRisk = self.cumulativeRisk - (stock.risk * numShares)
        self.portfolio.removeStockFromPortfolio(indexToSell, numShares)

    def updateRisk(self):
        # NOTE: change this to be represented as a fraction of money rather than fraction of shares
        print(self.portfolio.getPortfolioSize())
        self.aggregateRisk = self.cumulativeRisk / \
            (self.portfolio.getPortfolioSize())
