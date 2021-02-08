import time
from termcolor import colored
from parameters import cpu_core_mutex, task_mutex \
                ,system_total_time, system_total_time_mutex \
                ,increment_system_total_time



class CPUCore:
    def __init__(self, name):
        self.name = name
        self.idle_time = 0
        self.state = 'idle'
        self.running_task = None

    def set_running_task(self, task):
        cpu_core_mutex.acquire(blocking=False)
        self.running_task = task
        cpu_core_mutex.release()

    def set_state(self, state):
        cpu_core_mutex.acquire(blocking=False)
        self.state = state
        cpu_core_mutex.release()

    def get_state(self):
        cpu_core_mutex.acquire(blocking=False)
        state = self.state
        cpu_core_mutex.release()
        return state

    def process_task(self, task, resources, cpu_cores, time_quantum=None, queue=None, state='ready'):
        self.set_state('busy')
        self.set_running_task(task)

        task.set_state('running')
        task.allocate_resources(resources)

        if time_quantum == None:
            for _ in range(task.duration):
                time.sleep(1)
                # print_system_status(cpu_cores, resources)
                task.increment_cpu_time()
                self.idle_time += 1
                increment_system_total_time()

            task.set_state('done')
            task.free_resources(resources)

        else:
            remain_time = task.duration - task.cpu_time
            for _ in range(min(remain_time, time_quantum)):
                time.sleep(1)
                # print_system_status(cpu_cores, resources)
                task.increment_cpu_time()
                self.idle_time += 1
                increment_system_total_time()

            task.free_resources(resources)
            if task.cpu_time == task.duration:
                task.set_state('done')

            else:
                task.set_state(state)
                task.set_isAssigned(False)
                with task_mutex:
                    queue.append(task)

        print()
        print(colored('Task ' + task.name + ' current cputime: ', 'yellow')+ str(task.get_cpu_time()) \
            + '\n' + colored('Task ' + task.name + ' current state: ' , 'yellow')+ task.get_state())
        self.set_state('idle')
        self.set_running_task(None)