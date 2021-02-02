from threading import Thread, Lock, Semaphore, Timer
import threading
import time
import sys
from termcolor import colored


# Define Semaphore locks
resource_mutex = Semaphore()
task_mutex = Semaphore()
cpu_core_mutex = Semaphore()
system_total_time_mutex = Semaphore()


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
        return self.cpu_time


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



def hasEnoughResources(task, resources):
    isEnough = 1
    for res in task.get_required_resources():
        isEnough *= resources[res]

    return isEnough > 0


def print_cpu_cores_consumed_time(cpu_cores):
    print()
    print(colored('.: CPU Cores Status :.', 'yellow', attrs=('bold', )))
    for core in cpu_cores:
        print(colored(core.name + ': ', 'yellow') + str(core.idle_time) + ' secs!')

    print(colored('Total CPU time: ', 'yellow') + str(get_system_total_time()) + ' secs!')
    print()


def print_system_status(cpu_cores, resources):
    print()
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


def join_threads(threads):
    for th in threads:
        if th.is_alive():
            th.join()


def get_done_tasks_count(tasks):
    done_tasks_count = 0
    for task in tasks:
        if task.get_state() == 'done':
            done_tasks_count += 1
    return done_tasks_count


def increment_system_total_time():
    global system_total_time
    system_total_time_mutex.acquire(blocking=False)
    system_total_time += 1
    system_total_time_mutex.release()


def get_system_total_time():
    system_total_time_mutex.acquire(blocking=False)
    time = system_total_time
    system_total_time_mutex.release()
    return system_total_time

def FCFS():
    global ready
    global waiting
    threads = []
    while len(ready) > 0 or len(waiting) > 0:

        if len(waiting) > 0:
            task = waiting[0]
        else:
            task = ready[0]

        if hasEnoughResources(task, resources):
            while(not task.get_isAssigned()):
                for core in cpu_cores:
                    if core.get_state() == 'idle':
                        th = Thread(target=core.process_task, args=(task, resources, cpu_cores))
                        th.start()
                        threads.append(th)
                        task.set_isAssigned(True)
                        if task in ready:
                            ready.pop(0)
                        else:
                            waiting.pop(0)
                        break
        else:
            if task in ready:
                ready.pop(0)
            else:
                waiting.pop(0)
            waiting.append(task)


    join_threads(threads)

    print_cpu_cores_consumed_time(cpu_cores)
    exit(0)




def SJF():
    threads = []
    global ready
    ready = sorted(ready, key=lambda item: item.duration)
    while len(ready) > 0 or len(waiting) > 0:

        if len(waiting) > 0:
            task = waiting[0]
        else:
            task = ready[0]

        if hasEnoughResources(task, resources):
            while(not task.get_isAssigned()):
                for core in cpu_cores:
                    if core.get_state() == 'idle':
                        th = Thread(target=core.process_task, args=(task, resources, cpu_cores))
                        th.start()
                        threads.append(th)
                        task.set_isAssigned(True)
                        if task in ready:
                            ready.pop(0)
                        else:
                            waiting.pop(0)
                        break
        else:
            if task in ready:
                ready.pop(0)
            else:
                waiting.pop(0)
            waiting.append(task)


    join_threads(threads)

    print_cpu_cores_consumed_time(cpu_cores)
    exit(0)




def RoundRobin(time_quantum):
    threads = []
    tasks = ready.copy()

    while get_done_tasks_count(tasks) < tasks_count:
        isDone = True
        if len(waiting) > 0:
            task = waiting[0]
            isDone = False
        elif len(ready) > 0:
            task = ready[0]
            isDone = False

        if not isDone:
            if hasEnoughResources(task, resources):
                while(not task.get_isAssigned()):
                    for core in cpu_cores:
                        if core.get_state() == 'idle':
                            th = Thread(target=core.process_task, args=(task, resources, cpu_cores, time_quantum, ready))
                            task.set_isAssigned(True)
                            if task in ready:
                                ready.pop(0)
                            else:
                                waiting.pop(0)
                            th.start()
                            threads.append(th)
                            break
            else:
                if task in ready:
                    ready.pop(0)
                else:
                    waiting.pop(0)
                waiting.append(task)

    join_threads(threads)

    print_cpu_cores_consumed_time(cpu_cores)
    exit(0)




def multilevel_feedback_queue(queues_number, queues_time_quantum):
    queues = []
    for i in range(queues_number):
        queues.append([])
    queues[0] = ready
    queue_index = 0
    threads = []
    tasks = ready.copy()
    counter = 0
    while get_done_tasks_count(tasks) < tasks_count:
        isDone = True
        if len(waiting) > 0:
            task, queue_index = waiting[0]
            isDone = False
        else:
            for i in range(queues_number, 0, -1):
                if counter % (queues_number * i) == 0 and len(queues[i-1]) > 0:
                    task = queues[i-1][0]
                    queue_index = i-1
                    isDone = False
                    break
        counter += 1
        if not isDone:
            if hasEnoughResources(task, resources):
                while(not task.get_isAssigned()):
                    for core in cpu_cores:
                        if core.get_state() == 'idle':
                            next_level_queue_indx = min(queue_index+1, queues_number-1)
                            next_state = 'queue ' + str(next_level_queue_indx)
                            th = Thread(target=core.process_task, args=(task, resources, cpu_cores, \
                                queues_time_quantum[queue_index], queues[next_level_queue_indx], next_state))
                            task.set_isAssigned(True)

                            isWaiting = True
                            for i in range(queues_number):
                                if task in queues[i]:
                                    queues[i].pop(0)
                                    isWaiting = False
                            if isWaiting:
                                waiting.pop(0)
                            th.start()
                            threads.append(th)
                            break
            else:
                isWaiting = True
                for i in range(queues_number):
                    if task in queues[i]:
                        queues[i].pop(0)
                        isWaiting = False
                if isWaiting:
                    waiting.pop(0)

                waiting.append((task, queue_index))


    join_threads(threads)

    print_cpu_cores_consumed_time(cpu_cores)



def aging(queues):
    while len(queues[1])+len(queues[2]) > 0:
        with system_total_time_mutex:
            if (get_system_total_time()+1) % 15 == 0:
                with task_mutex:
                    while len(queues[2]) > 0:
                        task = queues[2].pop(0)
                        print('\n'+colored('Task ' + task.name + ' has been moved from queue_2 to queue_1!', 'yellow'))
                        task.set_priority(task.get_priority()-1)
                        queues[1].append(task)
        with system_total_time_mutex:
            if (get_system_total_time()+1) % 20 == 0:
                with task_mutex:
                    while len(queues[1]) > 0:
                        task = queues[1].pop(0)
                        print('\n'+colored('Task ' + task.name + ' has been moved from queue_1 to queue_0!', 'yellow'))
                        task.set_priority(task.get_priority()-1)
                        queues[0].append(task)


def seprate_tasks_by_priority(tasks):
    queues = []
    for i in range(3):
        queues.append([])

    for task in tasks:
        priority = task.get_priority()
        queues[priority-1].append(task)

    return queues


def multilevel_queue(): # TODO: Add aging to prevent starvation
    queues = seprate_tasks_by_priority(ready)
    queue_index = 0
    threads = []
    tasks = ready.copy()

    Thread(target=aging, args=(queues,)).start()

    while get_done_tasks_count(tasks) < tasks_count:

        isDone = True
        is_waiting = True
        if len(waiting) > 0:
            task = waiting[0]
            isDone = False
        else:
            for i in range(3):
                if len(queues[i]) > 0:
                    task = queues[i][0]
                    is_waiting = False
                    isDone = False
                    break

        if not isDone:
            if hasEnoughResources(task, resources):
                while(not task.get_isAssigned()):
                    for core in cpu_cores:
                        if core.get_state() == 'idle':
                            th = Thread(target=core.process_task, args=(task, resources, cpu_cores))
                            task.set_isAssigned(True)
                            with task_mutex:
                                if not is_waiting:
                                    for queue in queues:
                                        if task in queue:
                                            queue.pop(0)
                                            break
                                else:
                                    waiting.pop(0)
                            th.start()
                            threads.append(th)
                            break
            else:
                with task_mutex:
                    if queue_index != -1:
                        queues[queue_index].pop(0)
                    else:
                        waiting.pop(0)

                    waiting.append(task)


    join_threads(threads)
    print_cpu_cores_consumed_time(cpu_cores)



ready = []
waiting = []
cpu_cores = []
system_total_time = 0
resources = {}
tasks = []

print(colored('Tell me about the number of each resource:', 'yellow', attrs=('bold', )))
resources['A'] = int(input(colored('    A > ', 'yellow')))
resources['B'] = int(input(colored('    B > ', 'yellow')))
resources['C'] = int(input(colored('    C > ', 'yellow')))

tasks_count = int(input(colored('How many tasks do exist? ', 'yellow', attrs=('bold', ))))

for _ in range(tasks_count):
    task_info = input(colored('    > ', 'yellow')).split()
    task_name = task_info[0]
    task_type = task_info[1]
    task_duration = int(task_info[2])
    task = Task(task_name, task_type, task_duration)
    tasks.append(task)
    ready.append(task)


for i in range(1):
    cpu_cores.append(CPUCore('core {}'.format(i+1)))



# fcfs_thread = Thread(target=FCFS)
# fcfs_thread.start()
# fcfs_thread.join()

# sjf_thread = Thread(target=SJF)
# sjf_thread.start()
# sjf_thread.join()

# time_quantum = 2
# rr_thread = Thread(target=RoundRobin, args=(time_quantum, ))
# rr_thread.start()
# rr_thread.join()

mlf_thread = Thread(target=multilevel_feedback_queue, args=(3, [2,4,10]))
mlf_thread.start()
mlf_thread.join()

# mlq_thread = Thread(target=multilevel_queue)
# mlq_thread.start()
# mlq_thread.join()

sys.exit()