Check Point Management API Benckmarking Tool
Joe Dillig - Check Point Skunk Works 2019 - dilligj@checkpoint.com

Usage:
./APIBenchmark.py -m [ count -o <Number of Hosts> | -t time <Seconds> | delete ] -s <IP> -u <Username> -p <Password> -d <Domain>

Example: Benchmark Creation of 1000 Hosts
./APIBenchmark.py -m count -o 1000 -s 192.168..100.100 -u api_user -p api_password

Example: Benchmark Numbers of Hosts in 60 Seconds
./APIBenchmark.py -m time -t 60 -s 192.168..100.100 -u api_user -p api_password

Example: Delete Hosts Created For Benchmark
./APIBenchmark.py -m delete -s 192.168..100.100 -u api_user -p api_password

