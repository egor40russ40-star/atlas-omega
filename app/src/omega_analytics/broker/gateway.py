class BrokerGateway:
    def connect(self):
        return True

    def send_order(self, order):
        return {"status":"SIMULATED","order":order}
