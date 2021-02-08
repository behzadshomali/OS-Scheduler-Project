from threading import Thread, Lock, Semaphore, Timer
import threading
import time
import sys
from termcolor import colored
from task import Task
from cpuCore import CPUCore
from parameters import resources, tasks, ready, cpu_cores, tasks_count
from schedulers import FCFS, SJF, RoundRobin, multilevel_feedback_queue, multilevel_queue




if __name__ == '__main__':
    # print(colored('Tell me about the number of each resource:', 'yellow', attrs=('bold', )))
    # resources['A'] = int(input(colored('    A > ', 'yellow')))
    # resources['B'] = int(input(colored('    B > ', 'yellow')))
    # resources['C'] = int(input(colored('    C > ', 'yellow')))
    # tasks_count = int(input(colored('How many tasks do exist? ', 'yellow', attrs=('bold', ))))

    # for _ in range(tasks_count):
    #     task_info = input(colored('    > ', 'yellow')).split()
    #     task_name = task_info[0]
    #     task_type = task_info[1]
    #     task_duration = int(task_info[2])
    #     task = Task(task_name, task_type, task_duration)
    #     tasks.append(task)
    #     ready.append(task)

    # cpu_cores_count = int(input(colored('How many cpu cores do exist? ', 'yellow', attrs=('bold', ))))
    # for i in range(cpu_cores_count):
    #     cpu_cores.append(CPUCore('core {}'.format(i+1)))



    message = colored('Which algorithm are you going to run?\n\n', 'yellow', attrs=('bold', )) + \
            colored('    FCFS: ', 'yellow', attrs=('bold', )) + colored('First Come First Service\n', 'yellow') + \
            colored('    SJF: ', 'yellow', attrs=('bold', )) + colored('Shortest Job First\n', 'yellow') + \
            colored('    RR: ', 'yellow', attrs=('bold', )) + colored('Round Robin\n', 'yellow') + \
            colored('    MLF: ', 'yellow', attrs=('bold', )) + colored('Multi-level Feedback Queue\n', 'yellow') + \
            colored('    MLQ: ', 'yellow', attrs=('bold', )) + colored('Multi-level Queue (based on priorities)\n', 'yellow')


    algorithm = input(message)
    if algorithm.upper() == 'FCFS':
        fcfs_thread = Thread(target=FCFS)
        fcfs_thread.start()
        fcfs_thread.join()

    elif algorithm.upper() == 'SJF':
        sjf_thread = Thread(target=SJF)
        sjf_thread.start()
        sjf_thread.join()

    elif algorithm.upper() == 'RR':
        time_quantum = int(input(colored('Please enter the desired time quantum: ', 'yellow', attrs=('bold',))))
        rr_thread = Thread(target=RoundRobin, args=(time_quantum, ))
        rr_thread.start()
        rr_thread.join()

    # elif algorithm.upper() == 'MLF':
    #     queues_num = int(input(colored('Please enter the number of the queues: ', 'yellow', attrs=('bold',))))
    #     time_quantums = list(map(int,input(colored('Respictively, enter time quantum associated with each queue: ', 'yellow', attrs=('bold',))).split(' ')))
    #     mlf_thread = Thread(target=multilevel_feedback_queue, args=(queues_num, time_quantums))
    #     mlf_thread.start()
    #     mlf_thread.join()

    elif algorithm.upper() == 'MLQ':
        mlq_thread = Thread(target=multilevel_queue)
        mlq_thread.start()
        mlq_thread.join()

    sys.exit()