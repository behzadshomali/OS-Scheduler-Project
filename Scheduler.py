from threading import Thread, Lock, Semaphore, Timer
import threading
import time
import sys
from termcolor import colored


resource_mutex = Semaphore()
task_mutex = Semaphore()

class Task:
    def __init__(self, name, type, duration, priority=None):
        self.name = name
        self.type = type
        self.duration = duration
        self.priority = priority
        self.state = 'ready'
        self.cpu_time = 0
        self.isAssigned = False


    def set_state(self, state):
        task_mutex.acquire(blocking=False)
        self.state = state
        task_mutex.release()


    def get_state(self):
        task_mutex.acquire(blocking=False)
        state = self.state
        task_mutex.release()
        return state


    def allocate_resources(self, resources):
        resource_mutex.acquire(blocking=False)
        for res in self.required_resources:
            resources[res] -= 1
        resource_mutex.release()


    def free_resources(self, resources):
        resource_mutex.acquire(blocking=False)
        for res in self.required_resources:
            resources[res] += 1
        resource_mutex.release()

    def get_required_resources(self):
        if type == 'X':
            return ['A', 'B']
        elif type == 'Y':
            return ['B', 'C']
        elif type == 'Z':
            return ['A', 'C']




cpu_core_mutex = Semaphore()

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


    def process_task(self, task, resources, cpu_cores, **kwargs):
        time_quantum = kwargs.get('time_quantum')
        ready = kwargs.get('ready')

        self.set_state('busy')
        self.set_running_task(task)

        task.set_state('running')
        task.allocate_resources(resources)

        if time_quantum != None:
            for _ in range(task.duration):
                time.sleep(1)
                print_system_status(cpu_cores, resources)
                task.cpu_time += 1
                self.idle_time += 1

            task.set_state('done')
            task.free_resources(resources)

        else:
            remain_time = task.duration - task.cpu_time
            for _ in range(min(remain_time, time_quantum)):
                time.sleep(1)
                print_system_status(cpu_cores, resources)
                task.cpu_time += 1
                self.idle_time += 1

            task.free_resources(resources)
            if task.cpu_time == task.duration:
                task.set_state('done')
            else:
                task.set_state('ready')
                if ready != None:
                    ready.append(task)

        self.set_state('idle')
        self.set_running_task(None)




def hasEnoughResources(task, resources):
    isEnough = 1
    for res in task.get_required_resources():
        isEnough *= resources[res]

    return isEnough > 0


def print_cpu_cores_consumed_time(cpu_cores):
    print(colored('.: CPU Cores Status :.', 'yellow', attrs=('bold', )))
    for core in cpu_cores:
        print(colored(core.name + ': ', 'yellow') + str(core.idle_time) + 'secs!')


def print_system_status(cpu_cores, resources):
    print(colored('.: System Status :.', 'yellow', attrs=('bold', )))
    cpu_core_mutex.acquire(blocking=False)
    for core in cpu_cores:
        print(colored(core.name + ':', 'yellow'), end=' ')
        if core.get_state() == 'idle':
            print('idle')
        else:
            print(core.running_task.name)
    cpu_core_mutex.release()

    resource_mutex.acquire(blocking=False)
    for res, cnt in resources.items():
        print(colored('Resource ' + res + ': ', 'yellow') + str(cnt))
    print()
    resource_mutex.release()


def FCFS(ready, cpu_cores, resources):
    threads = []
    while len(ready) > 0:
        task = ready[0]
        while(not task.isAssigned):
            if hasEnoughResources(task, resources):
                for core in cpu_cores:
                    if core.get_state() == 'idle':
                        th = Thread(target=core.process_task, args=(task, resources, cpu_cores))
                        th.start()
                        threads.append(th)
                        task.isAssigned = True
                        ready.pop(0)
                        break


    for th in threads:
        if th.is_alive():
            th.join()

    print_cpu_cores_consumed_time(cpu_cores)




def SJF(ready, cpu_cores, resources):
    threads = []
    ready = sorted(ready, key=lambda item: item.duration)
    while len(ready) > 0:
        task = ready[0]
        while(not task.isAssigned):
            if hasEnoughResources(task, resources):
                for core in cpu_cores:
                    if core.get_state() == 'idle':
                        th = Thread(target=core.process_task, args=(task, resources, cpu_cores))
                        th.start()
                        threads.append(th)
                        task.isAssigned = True
                        ready.pop(0)
                        break

    for th in threads:
        if th.is_alive():
            th.join()

    print_cpu_cores_consumed_time(cpu_cores)




ready = []
waiting = []
cpu_cores = []
resources = {}
tasks = []

print(colored('Tell me about the number of each resource:', 'yellow', attrs=('bold', )))
resources['A'] = int(input(colored('    A > ', 'yellow')))
resources['B'] = int(input(colored('    B > ', 'yellow')))
resources['C'] = int(input(colored('    C > ', 'yellow')))

tasks_count = int(input(colored('How many tasks do exist? ', 'yellow', attrs=('bold', ))))

for _ in range(tasks_count):
    task_info = input(colored('    > ', 'yellow'))
    task_name = task_info[0]
    task_type = task_info[1]
    task_duration = int(task_info[2])
    task = Task(task_name, task_type, task_duration)
    tasks.append(task)
    ready.append(task)


for i in range(6):
    cpu_cores.append(CPUCore('core {}'.format(i+1)))



# fcfs_thread = Thread(target=fcfs, args=(ready, cpu_cores, resources))
# fcfs_thread.start()
# # print_system_status, args=(cpu_cores, resources)
# fcfs_thread.join()

sjf_thread = Thread(target=SJF, args=(ready, cpu_cores, resources))
sjf_thread.start()

sjf_thread.join()
sys.exit()
