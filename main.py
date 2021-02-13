from threading import Thread, Lock, Semaphore, Timer
import threading
import time
import sys
from termcolor import colored
from task import Task
from cpuCore import CPUCore
import globals
from schedulers import FCFS, SJF, RoundRobin, \
    multilevel_feedback_queue, multilevel_queue



if __name__ == '__main__':
    message = colored('Which algorithm are you going to run?\n\n', 'yellow', attrs=('bold', )) + \
            colored('    FCFS: ', 'yellow', attrs=('bold', )) + colored('First Come First Service\n', 'yellow') + \
            colored('    SJF: ', 'yellow', attrs=('bold', )) + colored('Shortest Job First\n', 'yellow') + \
            colored('    RR: ', 'yellow', attrs=('bold', )) + colored('Round Robin\n', 'yellow') + \
            colored('    MLFQ: ', 'yellow', attrs=('bold', )) + colored('Multi-level Feedback Queue\n', 'yellow') + \
            colored('    MLQ: ', 'yellow', attrs=('bold', )) + colored('Multi-level Queue (based on priorities)\n', 'yellow') + \
            colored('  > ', 'yellow')


    # input the intended scheduler algorithm
    algorithm = input(message)


    # input the number of tasks and also each resource
    print(colored('Tell me about the number of each resource:', 'yellow', attrs=('bold', )))
    globals.resources['A'] = int(input(colored('    A > ', 'yellow')))
    globals.resources['B'] = int(input(colored('    B > ', 'yellow')))
    globals.resources['C'] = int(input(colored('    C > ', 'yellow')))
    tasks_count = int(input(colored('How many tasks do exist? ', 'yellow', attrs=('bold', ))))


    # input information and initial each task
    for _ in range(tasks_count):
        task_info = input(colored('    > ', 'yellow')).split()
        task_name = task_info[0]
        task_type = task_info[1]
        task_duration = int(task_info[2])
        task = Task(task_name, task_type, task_duration)
        globals.tasks.append(task)
        globals.ready.append(task)


    # input number of cpu-cores and instanciate them
    cpu_cores_count = int(input(colored('How many cpu cores do exist? ', 'yellow', attrs=('bold', ))))
    for i in range(cpu_cores_count):
        globals.cpu_cores.append(CPUCore('core {}'.format(i+1)))


    # schedule input tasks based on chosen scheduler algorithm
    if algorithm.upper() == 'FCFS':
        fcfs_thread = Thread(target=FCFS, args=(tasks_count,))
        fcfs_thread.start()
        fcfs_thread.join()

    elif algorithm.upper() == 'SJF':
        sjf_thread = Thread(target=SJF, args=(tasks_count,))
        sjf_thread.start()
        sjf_thread.join()

    elif algorithm.upper() == 'RR':
        time_quantum = int(input(colored('Please enter the desired time quantum: ', 'yellow', attrs=('bold',))))
        rr_thread = Thread(target=RoundRobin, args=(tasks_count, time_quantum))
        rr_thread.start()
        rr_thread.join()

    elif algorithm.upper() == 'MLFQ':
        queues_num = int(input(colored('Please enter the number of the queues: ', 'yellow', attrs=('bold',))))
        time_quantums = list(map(int, input(colored('Respectively, enter time quantum associated with each queue: ', 'yellow', attrs=('bold',))).split(' ')))
        mlf_thread = Thread(target=multilevel_feedback_queue, args=(tasks_count, queues_num, time_quantums))
        mlf_thread.start()
        mlf_thread.join()

    elif algorithm.upper() == 'MLQ':
        mlq_thread = Thread(target=multilevel_queue, args=(tasks_count,))
        mlq_thread.start()
        mlq_thread.join()

    sys.exit()