from parameters import task_mutex
from parameters import resource_mutex

class Task:
    def __init__(self, name, type, duration):

        self.name = name
        self.type = type
        self.duration = duration
        self.set_state('ready')
        self.cpu_time = 0
        self.set_isAssigned(isAssigned=False)
        self.set_priority()


    def set_priority(self, priority=None):
        task_mutex.acquire(blocking=False)
        if priority == None:
            if self.type == 'Z':
                self.priority = 1
            elif self.type == 'Y':
                self.priority = 2
            elif self.type == 'X':
                self.priority = 3
        else:
            self.priority = priority
        task_mutex.release()

    def get_priority(self):
        task_mutex.acquire(blocking=False)
        priority = self.priority
        task_mutex.release()
        return priority

    def set_state(self, state):
        task_mutex.acquire(blocking=False)
        self.state = state
        task_mutex.release()

    def get_state(self):
        task_mutex.acquire(blocking=False)
        state = self.state
        task_mutex.release()
        return state

    def set_isAssigned(self, isAssigned):
        task_mutex.acquire(blocking=False)
        self.isAssigned = isAssigned
        task_mutex.release()

    def get_isAssigned(self):
        task_mutex.acquire(blocking=False)
        isAssigned = self.isAssigned
        task_mutex.release()
        return isAssigned

    def get_required_resources(self):
        if self.type == 'X':
            return ('A', 'B')
        elif self.type == 'Y':
            return ('B', 'C')
        elif self.type == 'Z':
            return ('A', 'C')


    def increment_cpu_time(self):
        resource_mutex.acquire(blocking=False)
        self.cpu_time += 1
        resource_mutex.release()


    def get_cpu_time(self):
        resource_mutex.acquire(blocking=False)
        cpu_time = self.cpu_time
        resource_mutex.release()
        return cpu_time

    def allocate_resources(self, resources):
        resource_mutex.acquire(blocking=False)
        for res in self.get_required_resources():
            resources[res] -= 1
        resource_mutex.release()

    def free_resources(self, resources):
        resource_mutex.acquire(blocking=False)
        for res in self.get_required_resources():
            resources[res] += 1
        resource_mutex.release()