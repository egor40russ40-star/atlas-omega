class ResearchCommandCenter:
    def __init__(self):
        self.jobs=[]
        self.status='READY'

    def add_job(self, job):
        self.jobs.append(job)

    def launch(self):
        return {
            'status':'RUNNING',
            'jobs':len(self.jobs)
        }

    def report(self):
        return {
            'status':self.status,
            'jobs':self.jobs
        }
