class ExpectedValueCalculator:
    def calculate(self, win_rate, reward, loss):
        return win_rate * reward - (1-win_rate) * loss
