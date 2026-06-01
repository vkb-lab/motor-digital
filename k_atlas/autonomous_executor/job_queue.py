QUEUE = []

def enqueue_job(job: dict):
    QUEUE.append(job)
    return job

def list_jobs():
    return list(QUEUE)
