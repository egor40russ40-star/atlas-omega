class ResearchProgress:
    def __init__(self):
        self.total=0
        self.done=0

    def update(self, total, done):
        self.total=total
        self.done=done

    def status(self):
        return {
            'total': self.total,
            'done': self.done
        }
