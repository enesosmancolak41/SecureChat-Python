import time
import socket
import secrets
import threading
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# === 13. HAFTA KÜTÜPHANESİ VE ANAHTAR ===
# Şimdilik iki tarafın da bildiği 32 Byte'lık (256 Bit) sabit bir anahtar kullanıyoruz.
# (14. Haftada bu anahtarı RSA ile havadan gizlice takas edeceğiz!)
AES_SABIT_ANAHTAR = b'SiberGuvenlikVeKriptografi123456' 

def ekranı_temizle():
    print("\033[H\033[J", end="")

def guvenli_rastgele_sayi_uret():
    iv = secrets.token_hex(16)
    print(f"[TEST ÇIKTISI] Üretilen Güvenli IV (CSPRNG): {iv}")
    return iv

# === YENİ: ŞİFRELEME MOTORLARI ===
def aes_sifrele(acik_metin):
    # Her mesaj için yepyeni bir IV (Initialization Vector) üretiyoruz (CBC modunun şartı)
    iv = secrets.token_bytes(16)
    cipher = AES.new(AES_SABIT_ANAHTAR, AES.MODE_CBC, iv)
    
    # Türkçe karakterler için UTF-8 ve AES'in 16 byte bloğuna uyması için Padding
    sifreli_bytes = cipher.encrypt(pad(acik_metin.encode('utf-8'), AES.block_size))
    
    # IV ve şifreli veriyi birleştirip, ağda bozulmasın diye Base64'e çeviriyoruz
    sifreli_mesaj = base64.b64encode(iv + sifreli_bytes).decode('utf-8')
    return sifreli_mesaj

def aes_sifre_coz(sifreli_base64):
    try:
        sifreli_veri = base64.b64decode(sifreli_base64)
        iv = sifreli_veri[:16] # İlk 16 byte bizim IV'miz
        asil_sifre = sifreli_veri[16:] # Geri kalanı şifreli mesaj
        
        cipher = AES.new(AES_SABIT_ANAHTAR, AES.MODE_CBC, iv)
        acik_metin = unpad(cipher.decrypt(asil_sifre), AES.block_size).decode('utf-8')
        return acik_metin
    except Exception as e:
        return "[HATA] Şifre çözülemedi veya mesaj bozuldu!"

# === DİNLEME MOTORU (GÜNCELLENDİ) ===
def mesaj_dinle(baglanti, gonderen_isim):
    while True:
        try:
            # Base64 dizileri uzun olabileceği için recv boyutunu 4096 yaptık
            gelen_sifreli_veri = baglanti.recv(4096).decode('utf-8')
            if not gelen_sifreli_veri: 
                print(f"\n[-] {gonderen_isim} bağlantıyı kesti.")
                break
                
            # HOCAYA ŞOV KISMI: Ağdan geçen o çılgın şifreli veriyi ekrana basıyoruz
            print(f"\n[AĞDAN GELEN PAKET - BASE64]: {gelen_sifreli_veri}")
            
            # ŞİFREYİ ÇÖZ VE GÖSTER
            cozulmus_mesaj = aes_sifre_coz(gelen_sifreli_veri)
            print(f"[{gonderen_isim}]: {cozulmus_mesaj}")
            
        except Exception as e:
            print(f"\n[-] {gonderen_isim} ile iletişim koptu. ({e})")
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
        
        print("\nSİSTEM: Uçtan Uca Şifreli (AES-256) Sohbet Başladı! (Çıkmak için 'q' yazın)")
        print("="*60)
        
        dinleme_thread = threading.Thread(target=mesaj_dinle, args=(conn, "İstemci"))
        dinleme_thread.daemon = True
        dinleme_thread.start()
        
        # MESAJ GÖNDERME KISMI (GÜNCELLENDİ)
        while True:
            orijinal_mesaj = input()
            if orijinal_mesaj.lower() == 'q':
                break
            
            # Mesajı ağa vermeden önce AES ile şifreliyoruz!
            sifreli_paket = aes_sifrele(orijinal_mesaj)
            conn.send(sifreli_paket.encode('utf-8'))
            
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
        
        print("\n--- GÜVENLİK DOĞRULAMASI (HANDSHAKE) BAŞLADI ---")
        challenge_str = client_socket.recv(1024).decode('utf-8')
        challenge = int(challenge_str)
        print(f"[Client] Server'dan gelen rastgele sayı: {challenge}")
        
        response = challenge * 2 + 7
        print(f"[Client] Gizli işlem uygulandı ((sayı * 2) + 7). Gönderilen cevap: {response}")
        client_socket.send(str(response).encode('utf-8'))
        print("--- HANDSHAKE TAMAMLANDI ---\n")
        time.sleep(0.5)
        
        print("SİSTEM: Uçtan Uca Şifreli (AES-256) Sohbet Başladı! (Çıkmak için 'q' yazın)")
        print("="*60)
        
        dinleme_thread = threading.Thread(target=mesaj_dinle, args=(client_socket, "Server"))
        dinleme_thread.daemon = True
        dinleme_thread.start()
        
        # MESAJ GÖNDERME KISMI (GÜNCELLENDİ)
        while True:
            orijinal_mesaj = input()
            if orijinal_mesaj.lower() == 'q':
                break
            
            # Mesajı ağa vermeden önce AES ile şifreliyoruz!
            sifreli_paket = aes_sifrele(orijinal_mesaj)
            client_socket.send(sifreli_paket.encode('utf-8'))
            
    except Exception as e:
        print(f"\n[-] Bağlantı hatası: {e}")
        
    client_socket.close()

def ana_menu():
    while True:
        ekranı_temizle()
        print("="*60)
        print(" "*10 + "SECURECHAT v2.0 - AES-256 Şifreli Ağ Modülü")
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
