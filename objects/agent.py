from actions import Actions
from objects import portfolio, stock
from state import State


class Agent:
    def __init__(self, name, startingCash, stockList):
        self.name = name
        self.currentState = State(startingCash)
        self.lastState = self.currentState
        self.possibleStocks = stockList

    def assessActions(self):
        actionChoices = Actions(self.currentState, self.possibleStocks)
        action, stockForAction, numShares = actionChoices.getNextAction()

        if(action == 1):
            self.buy(stockForAction, numShares)
        elif(action == -1):
            self.sell(stockForAction, numShares)
        else:
            pass

    def reportState(self):
        print(self.currentState)

    def sell(self, stock, numShares):
        sellPrice = stock.price
        indexToSell = next((i for i, item in enumerate(
            self.currentState.portfolio.stockList) if item["stockObj"].tickerName == stock.tickerName), None)
        self.currentState.sell(indexToSell, numShares, sellPrice)

    def buy(self, stock, numShares):
        if(stock.price * numShares) < self.currentState.cash:
            self.currentState.buy(stock, numShares)
        else:
            print("Error: not enough cash to buy")
