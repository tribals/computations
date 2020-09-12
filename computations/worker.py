class TasksScheduler(object):
    def __init__(self, tasks_repository):
        self._tasks_repository = tasks_repository

    def enqueue(self, connection, computation_id):
        return 42
        # task = Task(computation_id)

        # task_id = self._tasks_repository.add(task)
