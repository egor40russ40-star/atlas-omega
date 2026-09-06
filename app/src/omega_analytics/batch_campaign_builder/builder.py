class BatchCampaignBuilder:
    def build(self, instruments, strategies, timeframes):
        tasks=[]
        for i in instruments:
            for s in strategies:
                for tf in timeframes:
                    tasks.append({
                        'instrument': i,
                        'strategy': s,
                        'timeframe': tf
                    })
        return tasks
