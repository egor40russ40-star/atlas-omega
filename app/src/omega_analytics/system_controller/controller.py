class SystemController:
    def __init__(self, components=None):
        self.components = components or []

    def health(self):
        return all(self.components) if self.components else True
