from termcolor import colored
from threading import Thread
import globals


# check whether there are enough resources
# for intended task or not
def hasEnoughResources(task, resources):
    isEnough = 1
    for res in task.get_required_resources():
        isEnough *= resources[res]

    return isEnough > 0


# simulates "Aging" procedure to prevent
# starvation for tasks that has lower prior
# campared to others. after each 15 and 20
# time-units tasks are popped from queue-2
# and queue-1 respectively and the are pushed
# to a higher prior queue
def aging(queues):
    while len(queues[1])+len(queues[2]) > 0:
        with globals.system_total_time_mutex:
            if (globals.system_total_time+1) % 15 == 0:
                with globals.task_mutex:
                    while len(queues[2]) > 0:
                        task = queues[2].pop(0)
                        print('\n'+colored('Task ' + task.name + ' has been moved from queue_2 to queue_1!', 'yellow'))
                        task.set_priority(task.priority-1)
                        queues[1].append(task)
        with globals.system_total_time_mutex:
            if (globals.system_total_time+1) % 20 == 0:
                with globals.task_mutex:
                    while len(queues[1]) > 0:
                        task = queues[1].pop(0)
                        print('\n'+colored('Task ' + task.name + ' has been moved from queue_1 to queue_0!', 'yellow'))
                        task.set_priority(task.priority-1)
                        queues[0].append(task)


# it devides tasks into different queues
# based on their type/priority
def seprate_tasks_by_priority(tasks):
    queues = []
    for i in range(3):
        queues.append([])

    for task in tasks:
        priority = task.priority
        queues[priority-1].append(task)

    return queues


# First Come First Service algorithm,
# it schedules the tasks based on their
# initial input order
def FCFS(tasks_count):
    threads = []
    while len(globals.ready) > 0 or len(globals.waiting) > 0:

        if len(globals.waiting) > 0:
            task = globals.waiting[0]
        else:
            task = globals.ready[0]

        if hasEnoughResources(task, globals.resources):
            while(not task.get_isAssigned()):
                for core in globals.cpu_cores:
                    if core.get_state() == 'idle':
                        th = Thread(target=core.process_task, args=(task, globals.resources, globals.cpu_cores))
                        th.start()
                        threads.append(th)
                        task.set_isAssigned(True)
                        if task in globals.ready:
                            globals.ready.pop(0)
                        else:
                            globals.waiting.pop(0)
                        break
        else:
            if task in globals.ready:
                globals.ready.pop(0)
            else:
                globals.waiting.pop(0)
            globals.waiting.append(task)

    globals.join_threads(threads)
    globals.print_cpu_cores_consumed_time(globals.cpu_cores)
    exit(0)


# Shortest Job First,
# it schedules the tasks based on their
# CPU burst-time. in this algorithm tasks
# are sorted ascending
def SJF(tasks_count):
    threads = []
    globals.ready = sorted(globals.ready, key=lambda item: item.duration)
    while len(globals.ready) > 0 or len(globals.waiting) > 0:

        if len(globals.waiting) > 0:
            task = globals.waiting[0]
        else:
            task = globals.ready[0]

        if hasEnoughResources(task, globals.resources):
            while(not task.get_isAssigned()):
                for core in globals.cpu_cores:
                    if core.get_state() == 'idle':
                        th = Thread(target=core.process_task, args=(task, globals.resources, globals.cpu_cores))
                        th.start()
                        threads.append(th)
                        task.set_isAssigned(True)
                        if task in globals.ready:
                            globals.ready.pop(0)
                        else:
                            globals.waiting.pop(0)
                        break
        else:
            if task in globals.ready:
                globals.ready.pop(0)
            else:
                globals.waiting.pop(0)
            globals.waiting.append(task)

    globals.join_threads(threads)
    globals.print_cpu_cores_consumed_time(globals.cpu_cores)
    exit(0)


# Round Robin,
# it assigns time-quantum to each process
# then if the process isn't done yet, it will
# be pushed to a queue and wait for its turn
# to get another time slice (time-quantum)
def RoundRobin(tasks_count, time_quantum):
    threads = []
    tasks = globals.ready.copy()
    while globals.get_done_tasks_count(tasks) < tasks_count:
        isDone = True
        if len(globals.waiting) > 0:
            task = globals.waiting[0]
            isDone = False
        elif len(globals.ready) > 0:
            task = globals.ready[0]
            isDone = False

        if not isDone:
            if hasEnoughResources(task, globals.resources):
                while(not task.get_isAssigned()):
                    for core in globals.cpu_cores:
                        if core.get_state() == 'idle':
                            th = Thread(target=core.process_task, args=(task, globals.resources, globals.cpu_cores, time_quantum, globals.ready))
                            task.set_isAssigned(True)
                            if task in globals.ready:
                                globals.ready.pop(0)
                            else:
                                globals.waiting.pop(0)
                            th.start()
                            threads.append(th)
                            break
            else:
                if task in globals.ready:
                    globals.ready.pop(0)
                else:
                    globals.waiting.pop(0)
                globals.waiting.append(task)

    globals.join_threads(threads)
    globals.print_cpu_cores_consumed_time(globals.cpu_cores)
    exit(0)


# Multilevel Feedback Queue,
# this algorithm contains several queues
# with different time-quantums. the priority
# of each queue is different from another one.
# if given time-quantum to the task is insufficient
# then it will be pushed to next level queue that
# has lower prior but a greater time-quantum. to
# prioritize each queue, I used a simple "counter"
# variable that each time is used to compute "%"
def multilevel_feedback_queue(tasks_count, queues_number, queues_time_quantum):
    queues = []
    for i in range(queues_number):
        queues.append([])
    queues[0] = globals.ready
    queue_index = 0
    threads = []
    tasks = globals.ready.copy()
    counter = 0
    while globals.get_done_tasks_count(tasks) < tasks_count:
        isDone = True
        if len(globals.waiting) > 0:
            task, queue_index = globals.waiting[0]
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
            if hasEnoughResources(task, globals.resources):
                while(not task.get_isAssigned()):
                    for core in globals.cpu_cores:
                        if core.get_state() == 'idle':
                            next_level_queue_indx = min(queue_index+1, queues_number-1)
                            next_state = 'queue ' + str(next_level_queue_indx)
                            th = Thread(target=core.process_task, args=(task, globals.resources, globals.cpu_cores, \
                                queues_time_quantum[queue_index], queues[next_level_queue_indx], next_state))
                            task.set_isAssigned(True)

                            isWaiting = True
                            for i in range(queues_number):
                                if task in queues[i]:
                                    queues[i].pop(0)
                                    isWaiting = False
                            if isWaiting:
                                globals.waiting.pop(0)
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
                    globals.waiting.pop(0)

                globals.waiting.append((task, queue_index))

    globals.join_threads(threads)
    globals.print_cpu_cores_consumed_time(globals.cpu_cores)
    exit(0)


# Multilevel Queue (based on tasks priorities),
# as there are 3 types of task in this program
# (X, Y, Z), there are 3 queues with different
# priorities
def multilevel_queue(tasks_count):
    queues = seprate_tasks_by_priority(globals.ready)
    queue_index = 0
    threads = []
    tasks = globals.ready.copy()

    Thread(target=aging, args=(queues,)).start()

    while globals.get_done_tasks_count(tasks) < tasks_count:

        isDone = True
        is_waiting = True
        if len(globals.waiting) > 0:
            task = globals.waiting[0]
            isDone = False
        else:
            for i in range(3):
                if len(queues[i]) > 0:
                    task = queues[i][0]
                    is_waiting = False
                    isDone = False
                    break

        if not isDone:
            if hasEnoughResources(task, globals.resources):
                while(not task.get_isAssigned()):
                    for core in globals.cpu_cores:
                        if core.get_state() == 'idle':
                            th = Thread(target=core.process_task, args=(task, globals.resources, globals.cpu_cores))
                            task.set_isAssigned(True)
                            with globals.task_mutex:
                                if not is_waiting:
                                    for queue in queues:
                                        if task in queue:
                                            queue.pop(0)
                                            break
                                else:
                                    globals.waiting.pop(0)
                            th.start()
                            threads.append(th)
                            break
            else:
                with globals.task_mutex:
                    if queue_index != -1:
                        queues[queue_index].pop(0)
                    else:
                        globals.waiting.pop(0)

                    globals.waiting.append(task)


    globals.join_threads(threads)
    globals.print_cpu_cores_consumed_time(globals.cpu_cores)