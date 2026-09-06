class RankingStorage:
    def __init__(self):
        self.rankings=[]

    def save(self, item):
        self.rankings.append(item)
