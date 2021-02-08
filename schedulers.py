from termcolor import colored
from threading import Thread
from parameters import ready, waiting \
    ,resources , cpu_cores, join_threads \
    ,get_done_tasks_count, system_total_time_mutex \
    ,task_mutex, print_cpu_cores_consumed_time \
    ,tasks_count, system_total_time



def hasEnoughResources(task, resources):
    isEnough = 1
    for res in task.get_required_resources():
        isEnough *= resources[res]

    return isEnough > 0


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
            if (system_total_time+1) % 15 == 0:
                with task_mutex:
                    while len(queues[2]) > 0:
                        task = queues[2].pop(0)
                        print('\n'+colored('Task ' + task.name + ' has been moved from queue_2 to queue_1!', 'yellow'))
                        task.set_priority(task.get_priority()-1)
                        queues[1].append(task)
        with system_total_time_mutex:
            if (system_total_time+1) % 20 == 0:
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