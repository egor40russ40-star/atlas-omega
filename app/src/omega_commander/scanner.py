import os


class ProjectScanner:

    def scan(self):
        modules = [
            "omega_analytics",
            "omega_market_brain",
            "omega_core",
            "omega_data"
        ]

        result = {}

        for module in modules:
            path = os.path.join("app", "src", module)
            result[module] = "FOUND" if os.path.exists(path) else "MISSING"

        return result