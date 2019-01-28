#!/usr/bin/python

import requests, json, os, urllib3, time, sys, argparse, curses

#Disable the SSL Cert warning on each requests call
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

version='1.0'

parser = argparse.ArgumentParser(prog='Check Point Management API Benchmark Tool '+version, usage='./APIBenchmark.py -m [ count -o <Number of Hosts> | -t time <Minutes> | delete ] -s <IP> -u <Username> -p <Password> -d <Domain>')

#Arguments
parser.add_argument('-m', '--mode', help='Running Mode [count | time | delete]', required=True)
parser.add_argument('-o', '--objects', help='Number of Hosts to Create (count mode)', required=False)
parser.add_argument('-t', '--time', help='Time in Minutes to Run (time mode)', required=False)
parser.add_argument('-s', '--server', help='Check Point Management Server Ip', required=True)
parser.add_argument('-u', '--user', help='Check Point API Username', required=True)
parser.add_argument('-p', '--password', help='Check Point API Password', required=True)
parser.add_argument('-d', '--domain', help='Check Point Management Domain (Required if Multi-Domain)', required=False)


#Parse and Store Args
args = parser.parse_args()
benchmark_mode = args.mode
benchmark_hosts = args.objects
benchmark_time= args.time
cp_server = args.server
cp_user = args.user
cp_pass = args.password
cp_domain = args.domain

a=1
b=1
c=1
d=1

#Check Point Management Server
cp_url='https://'+cp_server+'/web_api'
cp_sid=''
total_time=0
duplicate_objects=0
unique_objects=0

print '[+] Check Point Management API Benchmark Tool '+version
print '[+] Joe Dillig - Check Point Software 2018'


def AddHost(host_name,host_ip):
    global unique_objects
    global duplicate_objects

    url=cp_url+'/add-host'
    headers = {'Content-type': 'application/json', 'Accept': 'bla', 'X-chkp-sid': cp_sid}
    data = {'name':host_name, 'ip-address':host_ip, 'comments':'API Benchmark Host','color':'orange', 'set-if-exists':True}
    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
    hostreturn = json.loads(r.text)

    #print(hostreturn['meta-info']['lock'])
    #Object Validation (Did the object already exist?)
    try:
        if hostreturn['meta-info']['lock'] == 'locked by current session':
            duplicate_objects = duplicate_objects + 1
            #print(' -> Duplicate Host Exists!')
        else:
            unique_objects=unique_objects+1
            #print(' -> Unique Host Exists!')
    except:
        print('failed to get return data')

    #print(jsonreturn)

def DeleteHost(host_name):
    url=cp_url+'/delete-host'
    headers = {'Content-type': 'application/json', 'Accept': 'bla', 'X-chkp-sid': cp_sid}
    data = {'name':host_name}
    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)

try:
    #Login
    url=cp_url+'/login'
    headers = {'Content-type': 'application/json', 'Accept': 'bla'}
    data = {'user': cp_user, 'password': cp_pass, 'session-timeout': '3600', 'session-name': 'Management API Benchmark Tool'}
    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
    jsonreturn = json.loads(r.text)
    #print(jsonreturn)
    cp_sid = jsonreturn['sid']

    count=0

    if benchmark_mode == 'count':

        #Write Delete File Before Starting Benchmark
        f = open(".benchmark_delete", "w")
        f.write(benchmark_hosts)

        print '[+] Starting Benchmark (Count Mode)'
        print '    Objects: '+str(benchmark_hosts)

        progress=0
        total_time=0
        progress_increment = (100 / int(benchmark_hosts))
        obj_per_sec_count=0
        obj_per_sec_timer=0
        obj_per_sec_print=0
        stdscr = curses.initscr()
        while int(count) < int(benchmark_hosts):

            host_name='BenchmarkHost'+str(count)

            if d < 255:
                d=d+1
                host_ip = str(a)+"."+str(b)+"."+str(c)+"."+str(d)

                #Start Timers
                create_start = time.time() #Timer

                #Create Object
                AddHost(host_name,host_ip)

                #End Timers
                create_finish = time.time() #Timer finish

                #Calculate Time
                elapsed = create_finish - create_start
                total_time = total_time + elapsed

                obj_per_sec_timer = obj_per_sec_timer + elapsed
                if obj_per_sec_timer >= 1:
                    #Log and Reset Time Count
                    obj_per_sec_print = obj_per_sec_count
                    obj_per_sec_timer=0
                    obj_per_sec_count=0

                running_avg = count/float(total_time)
                count=count+1
                obj_per_sec_count=obj_per_sec_count+1

                progress = float(count) / float(benchmark_hosts) * 100

                #Progress Box
                stdscr.addstr(0, 0, "[+] Benchmark Running - Count Mode - "+str(benchmark_hosts)+' Objects')
                stdscr.addstr(1, 0, "    Objects Created: "+str(count))
                stdscr.addstr(2, 0, "    Progress: %.2f" % round(progress,2)+"%")
                stdscr.addstr(3, 0, "    Avg Time Per Object: %.2f" % round(elapsed,2)+" Seconds")
                stdscr.addstr(4, 0, "    Objects Per Second: "+str(obj_per_sec_print))
                stdscr.addstr(5, 0, "    Elapsed Time: %.0f" % round(total_time)+" Seconds")
                stdscr.addstr(6, 0, "    Unique Objects: "+str(unique_objects))
                stdscr.addstr(7, 0, "    Duplicate Objects: "+str(duplicate_objects))
                stdscr.refresh()

            elif c < 255:
                c=c+1
                d=1 #Reset D

            elif b < 255:
                b=b+1
                c=1 #reset c
                d=1 #reset d

            elif a < 255:
                a=a+1
                b=1 #reset b
                c=1 #reset c
                d=1 #reset d

    if benchmark_mode == 'time':

        print '[+] Starting Benchmark - Time Mode'
        print '    Time: '+str(benchmark_time)+' Seconds'

        total_time=0
        count=0
        obj_per_sec_count=0
        obj_per_sec_timer=0
        obj_per_sec_print=0

        stdscr = curses.initscr()
        time_mode_start = time.time()

        while True:

            host_name='BenchmarkHost'+str(count)

            if d < 255:
                d=d+1
                host_ip = str(a)+"."+str(b)+"."+str(c)+"."+str(d)

                create_start = time.time() #Timer
                AddHost(host_name,host_ip)
                create_finish = time.time() #Timer finish

                elapsed = create_finish - create_start
                total_time = total_time + elapsed

                if float(total_time) >= float(benchmark_time):
                    benchmark_hosts = count
                    break

                obj_per_sec_timer = obj_per_sec_timer + elapsed
                if obj_per_sec_timer >= 1:
                    #Log and Reset Time Count
                    obj_per_sec_print = obj_per_sec_count
                    obj_per_sec_timer=0
                    obj_per_sec_count=0

                #Progress Box
                stdscr.addstr(0, 0, "[+] Benchmark Running - Time Mode - "+str(benchmark_time)+' Seconds')
                stdscr.addstr(1, 0, "    Objects Created: "+str(count))
                stdscr.addstr(2, 0, "    Avg Time Per Object: %.2f" % round(elapsed,2)+" Seconds")
                stdscr.addstr(3, 0, "    Objects Per Second: "+str(obj_per_sec_print))
                stdscr.addstr(4, 0, "    Elapsed Time: %.0f" % round(total_time)+" Seconds")
                stdscr.addstr(5, 0, "    Unique Objects: "+str(unique_objects))
                stdscr.addstr(6, 0, "    Duplicate Objects: "+str(duplicate_objects))
                stdscr.refresh()

                count=count+1
                obj_per_sec_count=obj_per_sec_count+1

            elif c < 255:
                c=c+1
                d=1 #Reset D

            elif b < 255:
                b=b+1
                c=1 #reset c
                d=1 #reset d

            elif a < 255:
                a=a+1
                b=1 #reset b
                c=1 #reset c
                d=1 #reset d

            #Write delete file
            f = open(".benchmark_delete", "w")
            f.write(str(count))


    if benchmark_mode == 'delete':

        #Read .benchmark_delete file
        f = open(".benchmark_delete", "r")
        benchmark_hosts= f.read()

        obj_per_sec_count=0
        obj_per_sec_timer=0
        obj_per_sec_print=0
        stdscr = curses.initscr()
        print '[+] Deleting '+benchmark_hosts+' Benchmark Objects...'

        while int(count) < int(benchmark_hosts):

            host_name='BenchmarkHost'+str(count)
            DeleteHost(host_name)
            progress=count/100
            count=count+1

            progress = float(count) / float(benchmark_hosts) * 100

            #Progress Box
            stdscr.addstr(0, 0, "[+] Deleting Benchmark Objects")
            stdscr.addstr(1, 0, "    Objects Deleted: "+str(count))
            stdscr.addstr(2, 0, "    Progress: %.2f" % round(progress,2)+"%")
            stdscr.refresh()


        os.remove(".benchmark_delete")

except Exception as e:
    print('exception occured: {}'.format(e))
finally:
    curses.endwin()

avg_time=float(total_time) / float(benchmark_hosts)

print '[+] ########## Benchmark Results ##########'
print '[+] Objects Statistics'
print '    Created Objects: '+str(benchmark_hosts)
print '    Unique Objects: '+str(unique_objects)
print '    Duplicate Objects: '+str(duplicate_objects)

print '[+] Time Statistics'
print '    Total Run Time: '+str(round(total_time))+' seconds'
print '    Objects Per Second: '+str(obj_per_sec_print)
print '    Average Creation Time Per Object: %.2f' % round(avg_time,2)+' Seconds'

print '[+] Publish Statistics'


#Publish Session
publish_start = time.time()
url=cp_url+'/publish'
headers = {'Content-type': 'application/json', 'Accept': 'bla', 'X-chkp-sid': cp_sid}
r = requests.post(url, data='{}', headers=headers, verify=False)
jsonreturn = json.loads(r.text)


while True:
    url=cp_url+'/show-task'
    headers = {'Content-type': 'application/json', 'Accept': 'bla', 'X-chkp-sid': cp_sid}
    data = {'task-id':jsonreturn['task-id']}
    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
    taskcheck = json.loads(r.text)

    if str(taskcheck['tasks'][0]['status']) == 'succeeded':
        break

publish_finish = time.time()
publish_elapsed = publish_finish - publish_start

print '    Publishing Time: %.2f' % round(publish_elapsed,2)+' Seconds'


#Logout
url=cp_url+'/logout'
headers = {'Content-type': 'application/json', 'Accept': 'bla', 'X-chkp-sid': cp_sid}
r = requests.post(url, data='{}', headers=headers, verify=False)
jsonreturn = json.loads(r.text)
print '    Logout - '+jsonreturn['message']

