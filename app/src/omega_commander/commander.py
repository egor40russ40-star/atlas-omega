from .scanner import ProjectScanner
from .diagnostics import Diagnostics
from .report_builder import ReportBuilder
from .permissions import PermissionManager


class Commander:

    def __init__(self):
        self.scanner = ProjectScanner()
        self.diagnostics = Diagnostics()
        self.report = ReportBuilder()
        self.permissions = PermissionManager()

    def health_check(self):
        result = {
            "mode": self.permissions.mode(),
            "scan": self.scanner.scan(),
            "diagnostics": self.diagnostics.run()
        }

        return self.report.build(result)