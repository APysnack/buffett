from objects.portfolio import Portfolio


class State:
    def __init__(self, cash, expectedReturn, aggregateRisk):
        self.cash = cash
        self.expectedReturn = expectedReturn
        self.aggregateRisk = aggregateRisk
        self.portfolio = Portfolio()

    def __str__(self):
        output = "[Cash: {}], [Expected Return: {}], [Aggregate Risk: {}], ".format(
            self.cash, self.expectedReturn, self.aggregateRisk)
        output = output + str(self.portfolio)
        return output
