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
        actionToTake = actionChoices.getNextAction()

    def reportState(self):
        print(self.currentState)

    def sellAll(self, stock):
        actionChoices = Actions(self.currentState, self.possibleStocks)
        actionChoices.sellAll(stock)
