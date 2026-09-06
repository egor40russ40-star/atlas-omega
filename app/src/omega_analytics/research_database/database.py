class ResearchDatabaseV2:
    def __init__(self):
        self.tables = {
            'instrument_registry': [],
            'strategy_versions': [],
            'backtest_results': [],
            'walk_forward_results': [],
            'strategy_ranking': [],
            'approved_models': []
        }

    def add(self, table, item):
        if table in self.tables:
            self.tables[table].append(item)

    def get(self, table):
        return self.tables.get(table, [])
