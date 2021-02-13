# OS Schedulers


### Files
* `main.py` : Contains main section of the program
* `task.py` : Illustrates class "Task". This class contains attributes such as: 
	* name
	* type (X, Y, Z)
	* duration (CPU burst-time)
	* cpu_time (how much time CPU has assigned time to this task)
	* priority
	* required resources: X: (A,B),  Y: (B,C), Z: (A,C)
* `cpuCore.py` : Illustrates class "CPUCore". This class contains attributes such as: 
	* name
	* idle_time (how much time this core has been busy)
	* state (busy, idle, running)
	* running_task (indicates he task that is processing by this CPU-core)
	* process_task() process the input task preemptive/none-preemptive
* `schedulers.py` : Contains different scheduling algorithms and also needed functions to run them
* `globals.py` : Contains globals variables and functions used in different files

### Algorithms
In this project I was supposed to implement some well-known OS scheduler algorithms. The implemented algorithms are as follows:
* `FCFS` : First Come First Service
* `SJF` : Shortest Job First
* `RR` : Round Robin
* `MLFQ` : Multilevel feedback queue
* `MLQ` : Multilevel Queue (based on priorities)


### How to run?
1. First of all you should run `main.py` with python 3.xx:
``` 
python3 main.py 
```
2. Choose the desired scheduler algorithm by typing its abbreviation:
`FCFS`, `SJF`, `RR`, `MLFQ`, `MLQ`
3.Specify the number of resources that are available in this system. You should enter the number of resources `A` , `B`, `C` respectively.
4. Enter the number of tasks that need to be processed
5. Enter the information about tasks (line-by-line) in the following format: `<name> <type> <duration>`
6. Enter the intended number of CPU-cores
7. In case that selected scheduler algorithm needs more parameters to be specified such as time-quantum or number of queues, you'll be asked to enter them at this step, otherwise algorithm starts working!


### Extra information
* In this program, tasks are fed to system at the first step which means tasks will not be added to system while CPU is processing
* One of the main advantages of this program is `multithreading`! It allows tasks to be processed by different CPU-cores simultaneously. So to be able to run this program you should have installed `threading` module
* To be able to use advantages of multi-threading, I used different `Semaphore`s
* This project was done as my final project of `Operating Systems` course in semester 5
