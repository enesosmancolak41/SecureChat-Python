import time
import socket
import secrets
import threading # Çift yönlü iletişim (Full-Duplex) için eklendi

def ekranı_temizle():
    print("\033[H\033[J", end="")

def guvenli_rastgele_sayi_uret():
    iv = secrets.token_hex(16)
    print(f"[TEST ÇIKTISI] Üretilen Güvenli IV (CSPRNG): {iv}")
    return iv

# Yeni Özellik: Arka planda sürekli çalışıp mesajları yakalayacak olan bağımsız bölüm
def mesaj_dinle(baglanti, gonderen_isim):
    while True:
        try:
            mesaj = baglanti.recv(1024).decode('utf-8')
            if not mesaj: 
                print(f"\n[-] {gonderen_isim} bağlantıyı kesti.")
                break
            print(f"\n[{gonderen_isim}]: {mesaj}")
        except:
            print(f"\n[-] {gonderen_isim} ile iletişim koptu.")
            break

def server_baslat():
    host = '0.0.0.0' 
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    
    print(f"\n[*] {port} portu dinleniyor. Gelen bağlantı bekleniyor...")
    conn, addr = server_socket.accept()
    print(f"[+] Bağlantı sağlandı! Gelen adres: {addr}\n")
    
    # --- HANDSHAKE BAŞLADI ---
    print("--- GÜVENLİK DOĞRULAMASI (HANDSHAKE) BAŞLADI ---")
    challenge = secrets.randbelow(100)
    print(f"[Server] İstemciye gönderilen rastgele sayı: {challenge}")
    conn.send(str(challenge).encode('utf-8'))
    
    cevap = conn.recv(1024).decode('utf-8')
    print(f"[Server] İstemciden gelen işlem görmüş cevap: {cevap}")
    
    beklenen_cevap = str(challenge * 2 + 7) 
    
    if cevap == beklenen_cevap:
        print(f"[TEST SONUCU] BAŞARILI! (Beklenen: {beklenen_cevap} == Gelen: {cevap})")
        print("--- HANDSHAKE TAMAMLANDI ---\n")
        
        guvenli_rastgele_sayi_uret() 
        
        print("\nSİSTEM: Karşılıklı sohbet başladı! (Çıkmak için 'q' yazın)")
        print("="*60)
        
        # Dinleme işini arka plandaki Thread'e (ikinci beyne) devrediyoruz
        dinleme_thread = threading.Thread(target=mesaj_dinle, args=(conn, "İstemci"))
        dinleme_thread.daemon = True
        dinleme_thread.start()
        
        # Ana bölüm (birinci beyin) sadece bizim klavyeden yazdıklarımıza odaklanıyor
        while True:
            mesaj = input()
            if mesaj.lower() == 'q':
                break
            conn.send(mesaj.encode('utf-8'))
            
    else:
        print(f"[TEST SONUCU] BAŞARISIZ! (Beklenen: {beklenen_cevap} != Gelen: {cevap})")
        print("[-] Bağlantı reddedildi.")
        
    conn.close()
    input("\nMenüye dönmek için Enter'a basın...")

def client_baslat(ip_adres):
    port = 12345
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    print(f"\n[*] {ip_adres}:{port} adresine bağlanılıyor...")
    try:
        client_socket.connect((ip_adres, port))
        
        # --- HANDSHAKE BAŞLADI ---
        print("\n--- GÜVENLİK DOĞRULAMASI (HANDSHAKE) BAŞLADI ---")
        challenge_str = client_socket.recv(1024).decode('utf-8')
        challenge = int(challenge_str)
        print(f"[Client] Server'dan gelen rastgele sayı: {challenge}")
        
        response = challenge * 2 + 7
        print(f"[Client] Gizli işlem uygulandı ((sayı * 2) + 7). Gönderilen cevap: {response}")
        client_socket.send(str(response).encode('utf-8'))
        print("--- HANDSHAKE TAMAMLANDI ---\n")
        time.sleep(0.5)
        
        print("SİSTEM: Karşılıklı sohbet başladı! (Çıkmak için 'q' yazın)")
        print("="*60)
        
        # Dinleme işini arka plandaki Thread'e devrediyoruz
        dinleme_thread = threading.Thread(target=mesaj_dinle, args=(client_socket, "Server"))
        dinleme_thread.daemon = True
        dinleme_thread.start()
        
        # Ana bölüm sadece bizim klavyeden yazdıklarımıza odaklanıyor
        while True:
            mesaj = input()
            if mesaj.lower() == 'q':
                break
            client_socket.send(mesaj.encode('utf-8'))
            
    except Exception as e:
        print(f"\n[-] Bağlantı hatası.")
        
    client_socket.close()

def ana_menu():
    while True:
        ekranı_temizle()
        print("="*60)
        print(" "*10 + "SECURECHAT v1.5 - Çift Yönlü (Duplex) Ağ Modülü")
        print("="*60)
        print(" [1] Bağlantı Bekle (Server Modu)")
        print(" [2] Birine Bağlan (Client Modu)")
        print(" [3] Çıkış")
        print("="*60)

        secim = input("\nLütfen bir işlem seçin (1/2/3): ")
        if secim == '1': server_baslat()
        elif secim == '2': 
            ip = input("[>] IP adresi (Test için 127.0.0.1): ")
            client_baslat(ip)
        elif secim == '3': break

if __name__ == "__main__":
    ana_menu()