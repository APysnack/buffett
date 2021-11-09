from objects import portfolio
import state


class Actions:
    def __init__(self, state, possibleStocks):
        self.currentState = state
        self.possibleStocks = possibleStocks

    def buy(self, stock):
        numShares = 1
        self.currentState.buy(stock, numShares)

    def sell(self, indexToSell, numShares):
        self.currentState.sell(indexToSell, numShares)

    def hold(self, stock):
        pass

    def getNextAction(self):
        stockToBuy = self.possibleStocks[0]
        for stock in self.possibleStocks:
            if stock.risk < stockToBuy.risk:
                stockToBuy = stock
        print(f"buy {stockToBuy.tickerName}")
        self.buy(stockToBuy)

    # sell all shares of input stock e.g. sell all shares of AAPL
    def sellAll(self, stock):
        numShares = 1
        indexToSell = next((i for i, item in enumerate(
            self.currentState.portfolio.stockList) if item["stockObj"].tickerName == stock.tickerName), None)
        self.sell(indexToSell, numShares)
