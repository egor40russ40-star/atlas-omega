class ResearchControlPanel:
    def __init__(self):
        self.jobs = []
        self.mode = "RESEARCH"

    def menu(self):
        return [
            "1. Запустить анализ рынка",
            "2. Выбор инструментов",
            "3. Выбор стратегий",
            "4. Статус тестов",
            "5. Лучшие модели",
            "6. Отчёты",
            "7. Экспорт моделей"
        ]

    def add_job(self, job):
        self.jobs.append(job)

    def status(self):
        return {
            "mode": self.mode,
            "jobs": len(self.jobs)
        }
