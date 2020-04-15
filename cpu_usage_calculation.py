import os
import time
import signal
import subprocess


all_device_cpu_list = []
system_server_cpu_list = []

# get cpu info
def get_all_cpu_info(pid = 0 , device = -1):
    # pid : pid of system_server , default = 0
    # device : 0-oppo , 1-huawei

    all_device_total_list = []
    all_device_idle_list = []
    system_server_total_list = []
    system_server_idle_list = []
    timeout_seconds = 30

    pcpu = '-1'

    print "get_cpuinfo start"

    try:
        for k in range(5):
            ## all devices cpu info get
            data = []
            #cpu_cmd = 'ssh -q -o StrictHostKeyChecking=no %s cat /proc/stat |grep -w cpu' % ip
            cpu_cmd = "adb shell cat /proc/stat |grep -w cpu"

            # res = os.popen(cpu_cmd, ).read().split()
            res = timeout_Popen(cpu_cmd, timeout=timeout_seconds)
            res = res.stdout.read().split()
            print str(res)

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
            if pid > 0:
                system_data = []
                #cpu_cmd = 'ssh -q -o StrictHostKeyChecking=no %s cat /proc/stat |grep -w cpu' % ip
                cpu_cmd = "adb shell cat /proc/%d/stat" %pid

                res = timeout_Popen(cpu_cmd, timeout=timeout_seconds)
                res = res.stdout.read().split()
                print str(res)

                if not res:
                    print('ssh %s get cpu info failed')
                    return pcpu

                for i in res:
                    try:
                        if isinstance(eval(i), int):
                            system_data.append(i)
                    except:
                        continue

                if device == 0:
                    total_cpu_time = sum([int(i) for i in system_data])
                    system_server_total_list.append(total_cpu_time)
                    system_server_idle_list.append(int(system_data[3]))
                elif device == 1:
                    total_cpu_time = sum([int(i) for i in system_data])
                    system_server_total_list.append(total_cpu_time)
                    system_server_idle_list.append(int(system_data[3]))
                else:
                    total_cpu_time = sum([int(i) for i in system_data])
                    system_server_total_list.append(total_cpu_time)
                    system_server_idle_list.append(int(system_data[3]))                   
            # slepp 5s to take
            time.sleep(5)
    except:
        pass

    index = 0
    for total_index in all_device_total_list:
        if index == 0 :
            index += 1
            continue
        
        total = total_index - all_device_total_list[index-1]
        idle = all_device_idle_list[index] - all_device_idle_list[index-1]
        pcpu = str(round(100 * (total - idle) / total, 2))
        all_device_cpu_list.append(pcpu)
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

# get_all_cpu_info : get cpu info , if pid is not null , get system_server cpu info either 
# pid : pid of system_server , default = 0
# device : 0-oppo , 1-huawei
all_cpu_usages = get_all_cpu_info(1842 ,0)

time_index = 0
print "All devices cpuinfo"
for cpu_usage in all_cpu_usages:
    print str(time_index) + "s to " + str(time_index + 5)+ "s" + "cpu usage :" + str(cpu_usage)
    time_index += 5