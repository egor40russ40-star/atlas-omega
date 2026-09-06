class RuntimeEngine:
    def __init__(self):
        self.mode = 'RESEARCH'
        self.running = False

    def start(self, mode='RESEARCH'):
        self.mode = mode
        self.running = True
        return self.mode

    def stop(self):
        self.running = False
        return 'STOPPED'
