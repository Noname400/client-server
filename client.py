import pip,os
import socket, threading, sys, subprocess, os, time
import shlex
from threading import Timer
from datetime import datetime
import requests
import logging
from logging import Formatter

try:
    import GPUtil
except:
    pip.main(['install','gputil'])
    import GPUtil
try:
    import psutil
except:
    pip.main(['install','psutil'])
    import psutil
    
current_path = os.path.dirname(os.path.realpath(__file__))
logger_info = logging.getLogger('INFO')
logger_info.setLevel(logging.INFO)
handler_info = logging.FileHandler(os.path.join(current_path, 'info.log'), 'a' , encoding ='utf-8')
handler_info.setFormatter(Formatter(fmt='[%(message)s'))
logger_info.addHandler(handler_info)

logger_err = logging.getLogger('ERROR')
logger_err.setLevel(logging.DEBUG)
handler_err = logging.FileHandler(os.path.join(current_path, 'error.log'), 'w' , encoding ='utf-8')
handler_err.setFormatter(Formatter(fmt='[%(message)s'))
logger_err.addHandler(handler_err)

host = ''
port = 2111
token = '5303833410:AAHYtEsd_YgEJ7i09sPcHFHMM735JC4MwQ'
channel_id = '@btcsearch'
GPU_TEMP = 85

class InfiniteTimer():
    def __init__(self, seconds, target):
        self._should_continue = False
        self.is_running = False
        self.seconds = seconds
        self.target = target
        self.thread = None

    def _handle_target(self):
        self.is_running = True
        self.target()
        self.is_running = False
        self._start_timer()

    def _start_timer(self):
        if self._should_continue: # Code could have been running when cancel was called.
            self.thread = Timer(self.seconds, self._handle_target)
            self.thread.start()

    def start(self):
        if not self._should_continue and not self.is_running:
            self._should_continue = True
            self._start_timer()
        else:
            print("Timer already started or running, please wait if you're restarting.")

    def cancel(self):
        if self.thread is not None:
            self._should_continue = False # Just in case thread is running and cancel fails.
            self.thread.cancel()
        else:
            print("Timer never started or failed to initialize.")

def check_temp():
    print('Check temp GPU ...')
    try:
        for gpu in GPUtil.getGPUs():
            print(f'{gpu.id}: {gpu.name} - {gpu.temperature}')
            if gpu.temperature > GPU_TEMP:
                send_telegram(f'{extract_ip()}: GPU {gpu.id} temp {gpu.temperature}')
    except:
        print('[E] Error: NO GPU')

def send_telegram(msg: str):
    try:
        requests.get(f'https://api.telegram.org/bot{token}/sendMessage', params=dict(
        chat_id=channel_id,
        text=msg))
    except:
        print(f'[E] Error send telegram.')

def date_str():
    now = datetime.now()
    return now.strftime("%m/%d/%Y, %H:%M:%S")

def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:       
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

def restart():
    rl = ''
    rl1=''
    list_file = os.listdir()
    for ld in list_file:
        if ld.find('Continue') > 0:
            ff = open(ld)
            rl = ff.readlines()
            for src in rl:
                print(f'проверочная строка {src}')
                if src.find("wif500-30xx.exe") >= 0: rl1 = src.replace("wif500-30xx.exe", "./wif500_86")
                if src.find("wif500-20xx.exe") >= 0: rl1 = src.replace("wif500-20xx.exe", "./wif500_86")
                if src.find("WifSolverCuda.exe") >= 0: rl1 = src.replace("WifSolverCuda.exe", "./wif500_86")
                if src.find("wif500_86") >= 0: rl1 = src.replace("wif500_86", "./wif500_86")
            
            prog = f'screen -dmS wif {rl1}'
            args = shlex.split(prog)
            ff.close()
            print(f'Команда на запуск ушла - {prog}')
            try:
                result = subprocess.run(args)
            except:
                print('[E] ERROR run application')
                logger_err.error(f'[E] {extract_ip()} | ERROR run application')
            finally:
                time.sleep(5)
            if result.returncode !=0: 
                print('[E] ERROR run application')
                logger_err.error(f'[E] {extract_ip()} | ERROR run application')
            else:
                res = stat()
                print(f'[I] {extract_ip()} | Programm wif500_86 run, total processes {res}')
                logger_info.info(f'[I] {extract_ip()} | Programm wif500_86 run, total processes {res}')
                logger_info.info(f'[I] {prog}')

def runing(cmd):
    prog = f'screen -dmS wif ./wif500_86 -range {cmd}'
    args = shlex.split(prog)
    print(prog)
    try:
        result = subprocess.run(args)
    except:
        print('[E] ERROR run application')
        logger_err.error(f'[E] {extract_ip()} | ERROR run application')
        return f'[E] {extract_ip()} | ERROR run application'
    finally:
        time.sleep(5)
    if result.returncode !=0: 
        print('[E] ERROR run application')
        logger_err.error(f'[E] {extract_ip()} | ERROR run application')
        return f'[E] {extract_ip()} | ERROR run application'
    else:
        res = stat()
        print(f'[I] {extract_ip()} | Programm wif500_86 run, total processes {res}')
        logger_info.info(f'[I] {extract_ip()} | Programm wif500_86 run, total processes {res}')
        logger_info.info(f'[I] {prog}')
        return f'[I] {extract_ip()} | Programm wif500_86 run, total processes {res}'

def find_file():
    check_file = os.path.exists('FOUND.txt')
    if check_file: return f'[F] {extract_ip()} | File found'
    else: return f'[I] {extract_ip()} | File NOT found'

def stat():
    cou = 0
    for proc in psutil.process_iter():
        name = proc.name()
        if name == "wif500_86":
            cou += 1
    return f'[I] {extract_ip()} | Run wif500_86 count: {cou}'

if __name__ == "__main__":
    version = '2.3'
    print(f'START: {date_str()}')
    print(f'Version {version}')
    print(f'Ваш IP: {extract_ip()}')
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print ("[I] Socket successfully created")
    except socket.error as err:
        print ("[E] socket creation failed with error %s" %(err))
        logger_err.error("[E] socket creation failed with error %s" %(err))
    sock.bind((host, port))
    sock.listen(20)
    #global connection
    print('Start Timer')
    t = InfiniteTimer(60, check_temp)
    t.start()
    send_telegram(f'{date_str()} Client RUN ...')
    while True:
        print('[I] waiting for a connection...')
        connection, client_addres = sock.accept()    
        print(f'[I] connection from {client_addres}')
        while True:
            try:
                data = connection.recv(1024).decode('utf-8')
            except:
                pass
            if not data:
                #print(f'[I] no data from {client_address}')
                break

            if data == 'find':
                print('[I] Search file')
                res = find_file()
                print(res)
                connection.send(res.encode('utf-8'))
                
            elif data == 'stat':
                print('[I] Statistic')
                res = stat()
                print(res)
                connection.send(res.encode('utf-8'))

            elif data == 'restore':
                print('[I] Restore')
                restart()
                res = 'OK'
                print(res)
                connection.send(res.encode('utf-8'))

            elif data.find('start') >= 0:
                #print(f'Receive {data[6:]}')
                runing(data[6:])
                res = 'OK'
                connection.send(res.encode('utf-8'))

            elif data == 'ping':
                print('[I] Ping')
                res = f'Ping OK'
                print(res)
                connection.send(res.encode('utf-8'))

            else:
                connection.close()
                print (f'[I] Close connection from {client_addres}')
                break
