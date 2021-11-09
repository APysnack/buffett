from actions import Actions
from objects import portfolio, stock
from state import State


class Agent:
    def __init__(self, name, cash, stockList):
        self.name = name
        self.currentState = State(cash, 0, 0)
        self.lastState = self.currentState
        self.possibleStocks = stockList

    def assessActions(self):
        actionChoices = Actions(self.currentState, self.possibleStocks)
        actionToTake = actionChoices.getNextAction()

    def reportState(self):
        print(self.currentState)
