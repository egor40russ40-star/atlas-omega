class ResearchQueue:
    def __init__(self):
        self.tasks = []

    def add(self, task):
        self.tasks.append(task)

    def size(self):
        return len(self.tasks)
