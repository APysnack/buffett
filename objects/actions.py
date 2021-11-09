import state


class Actions:
    def __init__(self, state, possibleStocks):
        self.currentState = state
        self.possibleStocks = possibleStocks

    def buy(self, stock):
        self.currentState.cash = self.currentState.cash - stock.price
        self.currentState.portfolio.addStockToPortfolio(stock)
        self.currentState.aggregateRisk = self.currentState.aggregateRisk + stock.risk

    def sell(self, stock):
        pass

    def hold(self, stock):
        pass

    def getNextAction(self):
        stockToBuy = self.possibleStocks[0]
        print(f"buy {stockToBuy.tickerName}")
        for stock in self.possibleStocks:
            if stock.risk < stockToBuy.risk:
                stockToBuy = stock
        self.buy(stock)
