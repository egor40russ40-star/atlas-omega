class OrderLifecycle:
    def process(self, order):
        return {"order": order, "state": "PENDING"}
