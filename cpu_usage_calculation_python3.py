import os
import time
import signal
import subprocess
import argparse


all_device_cpu_list = []
system_server_cpu_list = []
CPU_COUNT = 8

# get cpu info
def get_all_cpu_info(system_server_pid = 0 , frequency = 5 , times = 20):
    # pid : pid of system_server , default = 0

    all_device_total_list = []
    all_device_idle_list = []
    system_server_total_list = []
    system_server_idle_list = []
    timeout_seconds = 30

    pcpu = '-1'

    
    range_times = int(times)/int(frequency)
    print("get_cpuinfo start" + " times = " + str(range_times))

    try:
        for k in range(range_times):
            ## all devices cpu info get
            data = []
            #cpu_cmd = 'ssh -q -o StrictHostKeyChecking=no %s cat /proc/stat |grep -w cpu' % ip
            cpu_cmd = "adb shell cat /proc/stat | grep -w cpu"

            # res = os.popen(cpu_cmd, ).read().split()
            res = timeout_Popen(cpu_cmd, timeout=timeout_seconds)
            res = res.stdout.read().split()
            print(str(res))

            if not res:
                print('ssh %s get cpu info failed')
                return pcpu

            for i in res:
                try:
                    if isinstance(eval(i), int):
                        data.append(i)
                except:
                    continue

            total_cpu_time = sum([int(i) for i in data])
            all_device_total_list.append(total_cpu_time)
            all_device_idle_list.append(int(data[3]))

            ## system server cpu info get
            if int(system_server_pid) > 0:
                system_data = []
                #cpu_cmd = 'ssh -q -o StrictHostKeyChecking=no %s cat /proc/stat |grep -w cpu' % ip
                cpu_cmd = "adb shell cat /proc/%s/stat" %system_server_pid

                res = timeout_Popen(cpu_cmd, timeout=timeout_seconds)
                res = res.stdout.read().split()
                print(str(res))

                if not res:
                    print('get cpu info failed')
                    return pcpu

                for i in res:
                    try:
                        if isinstance(eval(i), int):
                            system_data.append(i)
                    except:
                        continue

                # total_cpu_time = sum([int(i) for i in system_data])
                system_server_total_list.append(int(res[14]) + int(res[15])+ int(res[16])+ int(res[17]))
                print(str(system_server_total_list))
                # system_server_idle_list.append(int(system_data[3]))

            # slepp frequency(s) to take
            time.sleep(int(frequency))
    except:
        pass

    index = 0
    for total_index in all_device_total_list:
        if index == 0 :
            index += 1
            continue
        
        total = total_index - all_device_total_list[index-1]
        idle = all_device_idle_list[index] - all_device_idle_list[index-1]
        system_server_time = system_server_total_list[index] - system_server_total_list[index-1]

        pcpu = str(round(100 * (total - idle) / total, 2))
        sys = str(round(100 * system_server_time * CPU_COUNT / total,2 ))
        all_device_cpu_list.append(pcpu)
        system_server_cpu_list.append(sys)
        index += 1
    return all_device_cpu_list

# handle popen timeout:
def timeout_Popen(cmd, timeout=30):
    start = time.time()
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while process.poll() is None:     
        now = time.time()
        if now - start >= timeout:
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            return None
    return process

def getPidByName(process_name):
    if process_name is None:
        return 0
    timeout_seconds = 30
    cpu_cmd = "adb shell pidof %s" %process_name
    res = timeout_Popen(cpu_cmd, timeout=timeout_seconds)
    res = res.stdout.read().split()
    print(process_name + " pid =  " + str(res[0]))
    return res[0]

# get_all_cpu_info(pid , device) : get cpu info , if pid is not null , get system_server cpu info either 
# pid : pid of system_server , default = 0
# device : 0-oppo , 1-huawei

parser = argparse.ArgumentParser(description='Process cpuinfo')
parser.add_argument('-p', '--process_name', dest='process',
                    help='process to parse')
parser.add_argument('-f', '--frequency', dest='frequency',
                    help='time frequency , how long to take data ') 
parser.add_argument('-t', '--time', dest='time',
                    help='how long') 
args = parser.parse_args()
freq = args.frequency
times = args.time

pid = getPidByName(args.process)
all_cpu_usages = get_all_cpu_info(pid,freq,times)

time_index = 0
print("All devices cpuinfo")
for cpu_usage in all_cpu_usages:
    print(str(time_index) + "s to " + str(time_index + int(freq))+ "s" + "  cpu usage :" + str(cpu_usage))
    time_index += int(freq)

print('------------------------')
time_index = 0
print("SystemServer cpuinfo")
for cpu_usage in system_server_cpu_list:
    print(str(time_index) + "s to " + str(time_index + int(freq))+ "s" + "  cpu usage :" + str(cpu_usage))
    time_index += int(freq)