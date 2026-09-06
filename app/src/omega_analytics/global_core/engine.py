class GlobalCore:
    def __init__(self):
        self.modules=[]
        self.status='READY'
    def register(self,module):
        self.modules.append(module)
    def health(self):
        return {'status':self.status,'modules':len(self.modules)}
