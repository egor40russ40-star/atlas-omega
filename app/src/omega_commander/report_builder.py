class ReportBuilder:

    def build(self, data):
        return {
            "system": "ATLAS OMEGA COMMANDER",
            "version": "v1",
            "status": "ACTIVE",
            "report": data
        }