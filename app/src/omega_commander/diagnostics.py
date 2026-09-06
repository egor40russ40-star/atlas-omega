import sys


class Diagnostics:

    def run(self):
        return {
            "python": sys.version.split()[0],
            "status": "READY",
            "mode": "RESEARCH_ONLY"
        }