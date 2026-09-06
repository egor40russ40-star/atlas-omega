class AutoSelectionEngine:
    def select(self, strategies):
        return strategies[0] if strategies else None
