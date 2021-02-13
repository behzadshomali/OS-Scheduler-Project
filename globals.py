from threading import Semaphore
from termcolor import colored


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

def increment_system_total_time():
    global system_total_time
    system_total_time_mutex.acquire(blocking=False)
    system_total_time += 1
    system_total_time_mutex.release()

def get_system_total_time():
    system_total_time_mutex.acquire(blocking=False)
    time = system_total_time
    system_total_time_mutex.release()
    return time

def join_threads(threads):
    for th in threads:
        if th.is_alive():
            th.join()

def get_done_tasks_count(tasks):
    global task_mutex
    done_tasks_count = 0
    for task in tasks:
        task_mutex.acquire(blocking=False)
        if task.state == 'done':
            done_tasks_count += 1
        task_mutex.release()
    return done_tasks_count


if __name__ == 'globals':
    resource_mutex = Semaphore()
    task_mutex = Semaphore()
    cpu_core_mutex = Semaphore()
    system_total_time_mutex = Semaphore()
    system_total_time_mutex.acquire()

    ready = []
    waiting = []
    cpu_cores = []
    resources = {}
    tasks = []
    system_total_time = 0