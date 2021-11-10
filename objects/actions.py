from objects import portfolio
import state


class Actions:
    def __init__(self, state, possibleStocks):
        self.currentState = state
        self.possibleStocks = possibleStocks

    def getNextAction(self):
        stockForAction = self.possibleStocks[0]
        for stock in self.possibleStocks:
            if stock.risk < stockForAction.risk:
                stockForAction = stock
        action = 1
        numShares = 20
        return action, stockForAction, numShares
