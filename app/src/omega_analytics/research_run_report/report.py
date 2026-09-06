class ResearchRunReport:
    def build(self, results):
        return {
            'total_tasks': len(results),
            'completed': len([r for r in results if r.get('status') == 'COMPLETED'])
        }
