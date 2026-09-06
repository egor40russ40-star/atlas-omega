class MassResearchRunner:
    def run(self, instruments, strategies):
        return [
            {'instrument': i, 'strategy': s, 'status':'QUEUED'}
            for i in instruments
            for s in strategies
        ]
