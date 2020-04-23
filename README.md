# Android&&Linux  Cpu Usage Calculation

# 整机 cpu 使用率计算

数据来源 ： /proc/stat （具体信息可以参考这里 http://man7.org/linux/man-pages/man5/proc.5.html ）

```shell
$ adb shell cat /proc/stat
cpu  24296 3660 18105 899033 640 3576 2202 0 0 0
cpu0 3473 285 3485 105976 58 1911 1120 0 0 0
cpu1 3180 292 3299 110424 75 523 384 0 0 0
cpu2 4209 760 3152 109585 68 501 340 0 0 0
cpu3 3860 790 3005 110329 54 426 276 0 0 0
cpu4 2120 416 1442 115725 100 65 21 0 0 0
cpu5 2015 454 1257 115964 81 74 38 0 0 0
cpu6 3153 394 1358 114858 123 41 10 0 0 0
cpu7 2284 266 1104 116170 78 33 8 0 0 0
intr 2389074 0 0 0 0 492483 0 152708 42 1121 52561 0 0 0 1349 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 6396 15 52113 0 0 0 0 0 0 0 2 0 120654 2800 38 17712 28640 0 716 0 0 0 0 24 0 1957 6038 0 0 0 0 0 0 80 61 76 71 62 61 136 89 13 0 0 0 0 0 0 0 0 16865 0 0 0 0 0 0 0 0 0 0 0 823 0 0 0 0 0 0 0 0 0 0 141 461 0 1 17278 0 0 0 0 0 2289 0 0 0 0 0 0 0 0 0 0 9216 237 0 0 3 0 3 0 0 0 0 0 0 0 0 0 0 2 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 31249 0 0 0 4 0 4554 81 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2233 15 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
ctxt 3555767
btime 1586953851
processes 11046
procs_running 4
procs_blocked 0
softirq 1279600 718 431045 9410 31637 11581 0 106547 338769 0 349893
```

## 数据分析

其中第一行 ：cpu  24296 3660 18105 899033 640 3576 2202 0 0 0
|参数  |解析（单位：jiffies）|  原文解释 |
| ----------   | -----------: | --------|
|user (24296) |    从系统启动开始累计到当前时刻，处于用户态的运行时间，不包含 nice值为负进程。|Time spent in user mode |
|nice (3660)   |   从系统启动开始累计到当前时刻，nice值为负的进程所占用的CPU时间|Time spent in user mode with low priority(nice) |
|system (18105)|  从系统启动开始累计到当前时刻，处于核心态的运行时间|Time spent in system mode |
|idle (899033) |  从系统启动开始累计到当前时刻，除IO等待时间以外的其它等待时间 | Time spent in the idle task.  This value should be USER_HZ times the second entry in the /proc/uptime pseudo-file|
|iowait (640)| 从系统启动开始累计到当前时刻，IO等待时间(since 2.5.41)|Time waiting for I/O to complete |
|irq (3576)     | 从系统启动开始累计到当前时刻，硬中断时间(since 2.6.0-test4)| Time servicing interrupts|
|softirq (2202)   |   从系统启动开始累计到当前时刻，软中断时间(since 2.6.0-test4)|Time servicing softirqs. |

那么总的 cpu 时间 totalCpuTime = user + nice + system + idle + iowait + irq + softirq 

## 使用率计算

取一段时间内的 两份数据  totalCpuTime 和 idle time

1. totalCpuTimeA ，idleA
2. totalCpuTimeB ，idleB

计算这一段时间内的 cpu 使用率：

cpu 使用率 = ((totalCpuTimeB - totalCpuTimeA) - (idleB - idleA) ) / (totalCpuTimeB - totalCpuTimeA) * 100

# 单个进程 cpu 使用率计算

数据来源 ： /proc/pid_of_process/stat

以华为手机 system_server 进程为例

```shell
$ adb shell cat /proc/1286/stat
1286 (system_server) S 889 889 0 0 -1 1077952832 404759 0 2760 0 9595 4059 0 0 18 -2 265 0 599 10783543296 86828 18446744073709551615 1 1 0 0 0 0 4612 0 1073794299 0 0 0 17 1 0 0 76 0 0 0 0 0 0 0 0 0 0
```

## 数据分析

说明：以下只解释对我们计算Cpu使用率有用相关参数

|参数|解释|原文|
|------|------  | ----|
|pid=1286|             进程号|The process ID.|
|comm=system_server| 进程名信息|The filename of the executable, in parentheses. This is visible whether or not the executable is swapped out|
|utime=9595 |          该任务在用户态运行的时间，单位为jiffies|Amount of time that this process has been scheduled in user mode, measured in clock ticks (divide by sysconf(_SC_CLK_TCK)).  This includes guest time, guest_time (time spent running a virtual CPU, see below), so that applications that are not aware of the guest time field do not lose that time from their calculations.|
|stime=4059    |       该任务在核心态运行的时间，单位为jiffies|Amount of time that this process has been scheduled in kernel mode, measured in clock ticks (divide by sysconf(_SC_CLK_TCK)).|
|cutime=0       |      用户态等待子进程的消耗，单位为jiffies|Amount of time that this process's waited-for chil‐ dren have been scheduled in user mode, measured in clock ticks (divide by sysconf(_SC_CLK_TCK)).  (See also times(2).)  This includes guest time, cguest_time (time spent running a virtual CPU, see  below)|
|cstime=0   |          内核态等待子进程的消耗，单位为jiffies|Amount of time that this process's waited-for chil‐ dren have been scheduled in kernel mode, measured in clock ticks (divide by sysconf(_SC_CLK_TCK))|

那么总的进程 cpu 时间 totalProcessCpuTime = utime + stime + cutime + cstime


## 使用率计算

取一段时间内的两份数据

1. totalCpuTimeA ，totalProcessCpuTimeA
2. totalCpuTimeB ，totalProcessCpuTimeB


cpu 使用率 = (totalProcessCpuTimeB - ，totalProcessCpuTimeA ) / (totalCpuTimeB - totalCpuTimeA) * 100 * CPU_CORE_COUNT

其中 CPU_CORE_COUNT 是手机的核数

# 示例


以一段复杂的操作为例，下面可以计算出这一段时间内的整机 cpu 使用率和 SystemServer(或者其他你比较关系的进程) 的 cpu 使用率


```shell
python cpu_usage_calculation.py -p system_server -f 2 -t 20
```

-p : 指定包名
-f : 指定抓取频率(单位为 s)
-t : 指定抓取时长(单位为 s)


通过使用率的对比就可以分析这一段时间内的负载，可以作为竞品对比或者优化验证

```shell
All devices cpuinfo (整机 cpu 使用率)
0s to 5s  cpu usage :98.0
5s to 10s  cpu usage :80.0
10s to 15s  cpu usage :57.0
15s to 20s  cpu usage :21.0

SystemServer cpuinfo (SystemServer  cpu 使用率)
0s to 5s  cpu usage :48.0
5s to 10s  cpu usage :35.0
10s to 15s  cpu usage :24.0
15s to 20s  cpu usage :2.0
```