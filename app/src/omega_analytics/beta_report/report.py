class BetaReport:
    def build(self, results):
        completed=len([r for r in results if r.get('status')=='COMPLETED'])
        return {
            'tasks': len(results),
            'completed': completed
        }
