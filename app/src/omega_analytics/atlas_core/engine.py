class AtlasEngine:
    def __init__(self, modules=None):
        self.modules = modules or []

    def analyze(self, data):
        result = data
        for module in self.modules:
            if hasattr(module, "analyze"):
                result = module.analyze(result)
        return result

    def health(self):
        return True
