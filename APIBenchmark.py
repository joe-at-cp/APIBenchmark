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

print '[+] Check Point Management API Benchmark Tool '+version
print '[+] Joe Dillig - Check Point Software 2018'


def AddHost(host_name,host_ip):
    url=cp_url+'/add-host'
    headers = {'Content-type': 'application/json', 'Accept': 'bla', 'X-chkp-sid': cp_sid}
    data = {'name':host_name, 'ip-address':host_ip, 'comments':'API Benchmark Host','color':'orange', 'set-if-exists':True}
    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
    #jsonreturn = json.loads(r.text)
    #print(jsonreturn)

def DeleteHost(host_name):
    url=cp_url+'/delete-host'
    headers = {'Content-type': 'application/json', 'Accept': 'bla', 'X-chkp-sid': cp_sid}
    data = {'name':host_name}
    r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)


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
    print '[-]   Objects: '+str(benchmark_hosts)

    progress=0
    total_time=0
    progress_increment = (100 / int(benchmark_hosts))
    stdscr = curses.initscr()
    while int(count) < int(benchmark_hosts):

        host_name='BenchmarkHost'+str(count)

        if d < 255:
            d=d+1
            host_ip = str(a)+"."+str(b)+"."+str(c)+"."+str(d)

            create_start = time.time() #Timer
            AddHost(host_name,host_ip)
            create_finish = time.time() #Timer finish
            elapsed = create_finish - create_start
            #print 'elapsed time:'+str(elapsed)
            #print 'totqal time:'+str(total_time)
            total_time = total_time + elapsed

            #progress=progress+progress_increment
            running_avg = count/float(total_time)
            count=count+1
            #print count

            progress = float(count) / float(benchmark_hosts) * 100

            #Progress Box
            stdscr.addstr(0, 0, "[+] Benchmark Running...")
            stdscr.addstr(1, 0, "    Objects Created: "+str(count))
            stdscr.addstr(2, 0, "    Progress: %.2f" % round(progress,2)+"%")
            stdscr.addstr(3, 0, "    Avg Time Per Object: %.2f" % round(elapsed,2)+" Seconds")
            stdscr.addstr(3, 0, "    Objects Per Second: %.2f" % round(elapsed,2)+" Seconds")
            stdscr.addstr(4, 0, "    Elapsed Time: %.0f" % round(total_time)+" Seconds")
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

    print '[+] Starting Benchmark (Time Mode)'

    total_time=0
    time_mode_start = time.time()

    while count < benchmark_hosts:

        host_name='BenchmarkHost'+str(count)

        if d < 255:
            d=d+1
            host_ip = str(a)+"."+str(b)+"."+str(c)+"."+str(d)

            create_start = time.time() #Timer
            AddHost(host_name,host_ip)

            create_finish = time.time() #Timer finish
            elapsed = create_finish - create_start
            total_time = total_time + elapsed

            if total_time >= benchmark_time:
                break

            count=count+1

            sys.stdout.write('[+] Progress: ?' )
            sys.stdout.write('    Objects Created: '+str(count)+'/'+str(benchmark_hosts))
            sys.stdout.write('    Elapsed Time:'+total_time)
            sys.stdout.flush()


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


if benchmark_mode == 'delete':

    #Read .benchmark_delete file
    f = open(".benchmark_delete", "r")
    benchmark_hosts= f.read()
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

avg_time=int(round(total_time, 2)) / int(benchmark_hosts)
curses.endwin()
print '[+] Total Time: '+str(round(total_time))+' seconds'
print '[+] Average Delete Time Per Host Object: '+str(avg_time)


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
    #print('Checking Publish Task: '+str(taskcheck['tasks'][0]['status'])+' Progress: '+str(taskcheck['tasks'][0]['progress-percentage']))
    #print('Checking Publish Task: '+taskcheck['tasks'][0])

    if str(taskcheck['tasks'][0]['status']) == 'succeeded':
        #print('task status='+str(taskcheck['tasks'][0]['status'])+'     Exiting loop')
        #print(str(taskcheck['tasks'][0]['status']))
        break

publish_finish = time.time()
publish_elapsed = publish_finish - publish_start
print '[+] Publishing Time: '+str(publish_elapsed)



#Logout
url=cp_url+'/logout'
headers = {'Content-type': 'application/json', 'Accept': 'bla', 'X-chkp-sid': cp_sid}
r = requests.post(url, data='{}', headers=headers, verify=False)
jsonreturn = json.loads(r.text)
print '[+] Logout - '+jsonreturn['message']

