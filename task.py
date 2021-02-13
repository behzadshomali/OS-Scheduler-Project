import globals

class Task:
    def __init__(self, name, type, duration):
        self.name = name
        self.type = type
        self.duration = duration
        self.set_state('ready')
        self.cpu_time = 0
        self.set_isAssigned(isAssigned=False)
        self.set_priority()

    # set priority based on the type of the task:
    # Z: high priority(1)
    # Y: medium priority(2)
    # X: low priority(3)
    def set_priority(self, priority=None):
        globals.task_mutex.acquire(blocking=False)
        if priority == None:
            if self.type == 'Z':
                self.priority = 1
            elif self.type == 'Y':
                self.priority = 2
            elif self.type == 'X':
                self.priority = 3
        else:
            self.priority = priority
        globals.task_mutex.release()

    def set_state(self, state):
        globals.task_mutex.acquire(blocking=False)
        self.state = state
        globals.task_mutex.release()

    def set_isAssigned(self, isAssigned):
        globals.task_mutex.acquire(blocking=False)
        self.isAssigned = isAssigned
        globals.task_mutex.release()

    def get_isAssigned(self):
        globals.task_mutex.acquire(blocking=False)
        isAssigned = self.isAssigned
        globals.task_mutex.release()
        return isAssigned

    # each type of task needs its associated
    # resources as follows:
    # X -> A,B
    # Y -> B,C
    # C -> A,C
    def get_required_resources(self):
        if self.type == 'X':
            return ('A', 'B')
        elif self.type == 'Y':
            return ('B', 'C')
        elif self.type == 'Z':
            return ('A', 'C')

    def increment_cpu_time(self):
        globals.resource_mutex.acquire(blocking=False)
        self.cpu_time += 1
        globals.resource_mutex.release()

    def allocate_resources(self, resources):
        globals.resource_mutex.acquire(blocking=False)
        for res in self.get_required_resources():
            resources[res] -= 1
        globals.resource_mutex.release()

    def free_resources(self, resources):
        globals.resource_mutex.acquire(blocking=False)
        for res in self.get_required_resources():
            resources[res] += 1
        globals.resource_mutex.release()