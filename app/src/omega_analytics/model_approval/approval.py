class ModelApproval:
    def approve(self, model, metrics=None):
        return {
            "model": model,
            "status": "APPROVED",
            "metrics": metrics or {}
        }
