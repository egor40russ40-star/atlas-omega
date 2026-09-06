from .models import LiveSignal

class LiveAnalyzer:
    def analyze(self, snapshot):
        if snapshot.support and snapshot.price <= snapshot.support * 1.01:
            return LiveSignal(snapshot.symbol, "LONG", "HIGH", "near_support")
        if snapshot.resistance and snapshot.price >= snapshot.resistance * 0.99:
            return LiveSignal(snapshot.symbol, "SHORT", "HIGH", "near_resistance")
        return LiveSignal(snapshot.symbol, "WAIT", "LOW", "no_setup")
