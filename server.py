import socket
import sys, subprocess
import time,os,threading
from threading import Timer
import requests
from datetime import datetime
import logging
from logging import Formatter

current_path = os.path.dirname(os.path.realpath(__file__))
logger_info = logging.getLogger('INFO')
logger_info.setLevel(logging.INFO)
handler_info = logging.FileHandler(os.path.join(current_path, 'info.log'), 'a' , encoding ='utf-8')
handler_info.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger_info.addHandler(handler_info)

logger_err = logging.getLogger('ERROR')
logger_err.setLevel(logging.DEBUG)
handler_err = logging.FileHandler(os.path.join(current_path, 'error.log'), 'w' , encoding ='utf-8')
handler_err.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger_err.addHandler(handler_err)

token = '5303833410:AAHYtEsd_YgEJ7i09sPcHFHMM735JC4MwQ'
channel_id = '@btcsearch'

def date_str():
    now = datetime.now()
    return now.strftime("%m/%d/%Y, %H:%M:%S")

def send_telegram(msg: str):
    try:
        requests.get(f'https://api.telegram.org/bot{token}/sendMessage', params=dict(
        chat_id=channel_id,
        text=msg))
    except:
        print(f'[E] Error send telegram.')
        logger_err.error(f'[E] Error send telegram.')

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
        if self._should_continue:
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

def save_done():
    x = open('done.txt','a')
    for line in done_list:
        x.write(line+'\n')
    x.close()

def save_cmd():
    x = open('cmd.txt','w')
    for line in cmd_list:
        x.write(line+'\n')
    x.close()

def send_stat():
    for line_ip in ip_list:
        try:
            connect(line_ip,'stat')
        except:
            print(f'[E] {line_ip} DOWN')
            logger_err.error(f'[E] {line_ip} DOWN')
            continue
        print(f'[I] {line_ip} UP')
        logger_info.info(f'[I] {line_ip} UP')
    sock.close()

def send_restore():
    for line_ip in ip_list:
        try:
            connect(line_ip,'restore')
        except:
            print(f'[E] {line_ip} DOWN')
            logger_err.error(f'[E] {line_ip} DOWN')
            continue
        print(f'[I] {line_ip} UP')
        logger_info.info(f'[I] {line_ip} UP')
    sock.close()

def send_start():
    del done_list[:]
    for line_ip in ip_list:
        try:
            connect(line_ip, 'ping')
        except:
            print(f'[E] {line_ip} DOWN')
            send_telegram(f'[E] Stat Error {line_ip} DOWN')
            logger_err.error(f'[E] Stat Error {line_ip} DOWN')
            continue
        print(f'[I] {line_ip} UP')
        print(f'количество карт: {card}')
        for i in range(card):
            print(f'позиция: {i}')
            line_cmd = cmd_list[i] #cmd_list.pop(position)
            print(f'{i} запуск {line_cmd}')
            done_list.append(f'{line_cmd} -d {i}')
            connect(line_ip, f'start {line_cmd} -d {i}')
            time.sleep(5)
            sock.close()
        del cmd_list[0:card]
    save_cmd()
    save_done()

def send_find():
    for line_ip in ip_list:
        try:
            connect(line_ip, 'find')
            sock.close()
        except:
            print(f'{line_ip} DOWN')
            send_telegram(f'[E] Find Error {line_ip} DOWN')
            logger_err.error(f'[E] Find Error {line_ip} DOWN')
            continue

def connect(host_src,msg):
    global sock
    host = host_src
    port = 2111
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    try:
        print(f'Отправлено: {host_src} | {msg}')
        sock.send(str.encode(msg))
        data = sock.recv(1024).decode('utf-8')
        print('[I] Принято: {!r}'.format(data))
           
        if data.find('Run wif500_86') >= 0:
            send_telegram(data)

        elif data.find('File found') >= 0:
           send_telegram(data)
    except:
        print("[E] Could not make a connection to the server")
        logger_err.error("[E] Could not make a connection to the server")
        input("Press enter to quit")
        sys.exit(0)
    return data.encode('utf-8')

if __name__ == "__main__":
    version = '2.2'
    if len (sys.argv) == 3:
        card = int(sys.argv[1])
        position = int(sys.argv[2])
    else:
        if len (sys.argv) < 3:
            print ("Ошибка. Слишком мало параметров.")
            sys.exit (1)

        if len (sys.argv) > 3:
            print ("Ошибка. Слишком много параметров.")
            sys.exit (1)

    send_telegram(f'{date_str()} Server RUN ...')
    print(f'START: {date_str()}')
    print(f'Version {version}')
    ip_list = []
    cmd_list = []
    done_list = []
    timer = False
    f = open('ip.txt', "r")
    while True:
        line = f.readline()
        if not line:
            break
        ip_list.append(line.strip())

    f = open('cmd.txt', "r")
    while True:
        line = f.readline()
        if not line:
            break
        cmd_list.append(line.strip())

    while True:
        message = input('ENTER command: stat, find, start, timer > ')
        if message == 'stat':
            send_stat()
        elif message == 'start':
            send_start()
            position = 0
        elif message == 'find':
            send_find()
        elif message == 'restore':
            send_restore()
        elif message == 'timer':
            if timer:
                print('STOP Timer')
                t.cancel()
            else:
                print('Start Timer')
                t = InfiniteTimer(1800, send_find)
                t.start()
                timer = True
        else: 
            print('WARNING!!!! command only: stat, find, start, timer')