import os


class DataAudit:

    def run(self):

        checks = {}

        paths = {
            "omega_data":
                "app/src/omega_data",

            "historical_engine":
                "app/src/omega_analytics/historical_data_engine",

            "historical_loader":
                "app/src/omega_analytics/historical_loader",

            "tinvest_adapter":
                "app/src/omega_analytics/tinvest"
        }

        for name, path in paths.items():
            checks[name] = (
                "FOUND"
                if os.path.exists(path)
                else "MISSING"
            )

        return {
            "DATA_AUDIT": "v1",
            "checks": checks
        }