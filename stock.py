class Stock:
    def __init__(self, ticker, name, low, high, delta):
        self.ticker = ticker
        self.name = name
        self.low = low
        self.high = high
        self.delta = delta

    def getTicker(self):
        return self.ticker

    def lowPrice(self):
        return self.low

    def highPrice(self):
        return self.high

    def getName(self):
        return self.getName()

    def getDelta(self):
        return self.getDelta()