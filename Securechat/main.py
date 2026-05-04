import os            # isletim sistemi komutlari (terminal temizleme vb.) icin
import sys           # programi tamamen sonlandirmak (exit) icin
import socket        # tcp/ip uzerinden ag paketleri gondermek/almak icin
import threading     # ayni anda hem mesaj okuyup hem yazabilmek (asenkron) icin
from datetime import datetime # log satirlarina zaman damgasi eklemek icin
import time          # islemler arasinda islemciyi ve agi senkronize etmek (delay) icin
import secrets       # kriptografik aciklari olmayan, donanimsal rastgele veri (csprng) uretimi icin
import base64        # raw byte (ikili) veriyi agda kaybolmamasi icin ascii karakterlere kodlamak icin
from Crypto.Cipher import AES, PKCS1_OAEP # simetrik (aes) ve asimetrik (rsa-oaep) sifreleme motorlari
from Crypto.PublicKey import RSA          # rsa anahtar cifti uretim sinifi
from Crypto.Hash import SHA256, HMAC      # veri butunlugu (hash) ve mesaj dogrulama (mac) algoritmalar
from Crypto.Util.Padding import pad, unpad # aes'in 16 byte blok zorunlulugunu saglamak icin dolgu fonksiyonlari

class SecureChat:
    def __init__(self):
        self.role = None              # programin host mu client mi olarak calistigini tutar
        self.PORT = 5555              # tcp soketinin dinleyecegi veya baglanacagi port numarasi
        self.conn = None              # aktif ag baglantisini (soket objesini) tutar
        self.AES_KEY = None           # veri trafigini sifreleyecek 256-bit simetrik anahtar (bos baslar)
        
        # rsa-2048 asimetrik anahtar ciftini ram uzerinde uretir (diske yazilmaz)
        self.rsa_key = RSA.generate(2048)
        self.private_key = self.rsa_key             # agdan gelen sifreli veriyi cozecek gizli anahtar
        self.public_key = self.rsa_key.publickey()  # karsi tarafa iletilecek acik anahtar
        self.partner_public_key = None              # karsi tarafin iletecegi acik anahtari tutacak degisken

    def clear_screen(self):
        # isletim sistemini tespit edip uygun terminal temizleme komutunu calistirir
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message, log_type="INFO"):
        # mevcut saati saat:dakika:saniye formatinda alir
        time_str = datetime.now().strftime("%H:%M:%S")
        # ekrana formatli bir sistem logu basar
        print(f"[{time_str}] [{log_type}] {message}")

    def display_message(self, sender, text):
        # gelen veya giden mesajlari saat bilgisiyle ekrana yazdirir
        time_str = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{time_str}] {sender} >> {text}")

    def generate_csprng(self):
        # 16 byte uzunlugunda kriptografik olarak guvenli rastgele hex string uretir
        return secrets.token_hex(16)

    def exchange_keys(self, is_host):
        self.log("RSA 2048-bit Anahtarları üretildi. Takas başlıyor...", "KRİPTO")
        time.sleep(0.5) # ag senkronizasyonu icin kisa bekleme

        try:
            if is_host:
                # 1. host kendi public key'ini byte formatinda karsi tarafa yollar
                self.conn.send(self.public_key.export_key())
                time.sleep(0.5)
                
                # 2. client'in gonderdigi public key byte dizisini agdan okur
                client_pub_data = self.conn.recv(4096)
                # alinan byte dizisini rsa public key objesine cevirir
                self.partner_public_key = RSA.import_key(client_pub_data)
                self.log("İstemcinin Public Key'i alındı.", "KRİPTO")

                # 3. oturum trafigini sifreleyecek asil 32 byte (256-bit) aes anahtarini uretir
                self.AES_KEY = secrets.token_bytes(32)

                # 4. rsa algoritmasi ve oaep padding standardi ile bir sifreleme objesi olusturur
                cipher_rsa = PKCS1_OAEP.new(self.partner_public_key)
                # aes anahtarini, karsi tarafin public key'i ile sifreler
                enc_session_key = cipher_rsa.encrypt(self.AES_KEY)
                
                # 5. rsa ile sifrelenmis aes anahtarini tcp soketi uzerinden agda iletir
                self.conn.send(enc_session_key)
                self.log("AES Session Key RSA ile şifrelenip iletildi.", "KRİPTO")
                time.sleep(0.5)
                return True
            else:
                # 1. client, host'un gonderdigi public key byte dizisini okur
                host_pub_data = self.conn.recv(4096)
                # diziyi rsa public key objesine donusturup kaydeder
                self.partner_public_key = RSA.import_key(host_pub_data)
                self.log("Host'un Public Key'i alındı.", "KRİPTO")
                time.sleep(0.5)

                # 2. client kendi public key'ini byte formatinda host'a yollar
                self.conn.send(self.public_key.export_key())
                time.sleep(0.5)

                # 3. host'tan gelen rsa ile sifrelenmis aes anahtarini byte dizisi olarak alir
                enc_session_key = self.conn.recv(4096)

                # 4. kendi private key'ini kullanarak oaep standardinda desifreleme objesi olusturur
                cipher_rsa = PKCS1_OAEP.new(self.private_key)
                # rsa sifresini cozerek orijinal 32 byte aes anahtarini elde eder
                self.AES_KEY = cipher_rsa.decrypt(enc_session_key)
                self.log("Şifreli AES Session Key başarıyla çözüldü.", "KRİPTO")
                return True
        except Exception as e:
            # key exchange (anahtar takasi) sirasinda hata olursa loglar ve false dondurur
            self.log(f"Anahtar takası başarısız: {e}", "HATA")
            return False

    def encrypt_message(self, plaintext):
        try:
            # cbc modunda kullanilacak 16 byte rastgele initialization vector (iv) uretir
            iv = secrets.token_bytes(16) 
            # aes-256 motorunu cbc modunda ve uretilen iv ile baslatir
            cipher = AES.new(self.AES_KEY, AES.MODE_CBC, iv)
            # string formundaki metni utf-8 byte'a cevirip 16 byte katlarina (pkcs7) tamamlar
            padded_data = pad(plaintext.encode('utf-8'), AES.block_size)
            # dolgulu metni aes algoritmasiyla sifreler
            ciphertext = cipher.encrypt(padded_data)
            
            # veri butunlugu icin hmac algoritmasini baslatir. girdi: iv + ciphertext
            hmac = HMAC.new(self.AES_KEY, iv + ciphertext, digestmod=SHA256)
            # hmac isleminden cikan 32 byte boyutundaki mesaji dogrulama kodunu alir
            signature = hmac.digest()
            
            # raw byte'lari (iv + sifreli metin + mac) birlestirip base64 string'e kodlar
            final_payload = base64.b64encode(iv + ciphertext + signature).decode('utf-8')
            # olusturulan tasima katmani verisini dondurur
            return final_payload
            
        except Exception as e:
            # sifreleme adimlarindan birinde hata olusursa yakalar
            self.log(f"Şifreleme hatası: {e}", "HATA")
            return None

    def decrypt_message(self, encrypted_b64):
        try:
            # agdan gelen base64 stringini tekrar raw byte formatina cevirir
            raw_data = base64.b64decode(encrypted_b64)
            
            # byte dizisinin son 32 byte'ini hmac mac (dogrulama kodu) olarak ayirir
            signature_received = raw_data[-32:] 
            # son 32 byte haricindeki kismi (iv + ciphertext) verinin govdesi olarak ayirir
            iv_and_cipher = raw_data[:-32]      
            # govdenin ilk 16 byte'ini initialization vector (iv) olarak okur
            iv = iv_and_cipher[:16]
            # govdenin geri kalan kismini sifreli ana metin (ciphertext) olarak okur
            ciphertext = iv_and_cipher[16:]
            
            # alinan govde uzerinden aes anahtari ile yepyeni bir hmac hesaplamasi baslatir
            hmac = HMAC.new(self.AES_KEY, iv_and_cipher, digestmod=SHA256)
            try:
                # hesaplanan hmac ile paketteki hmac'i karsilastirarak malleability kontrolu yapar
                hmac.verify(signature_received)
            except ValueError:
                # karsilasma basarisiz olursa veri manipule edilmis demektir, deşifrelemeyi reddeder
                return "❌ [GÜVENLİK İHLALİ] Bütünlük kontrolü başarısız! Mesaj ağda değiştirilmiş."
            
            # hmac basariliysa aes deşifreleme motorunu ayni iv ile baslatir
            cipher = AES.new(self.AES_KEY, AES.MODE_CBC, iv)
            # sifreyi cozer, pkcs7 dolgularini (unpad) kaldirir ve utf-8 string formatina cevirir
            plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size).decode('utf-8')
            # cozulmus orijinal duz metni (plaintext) dondurur
            return plaintext
            
        except Exception:
            # format hatasi (eksik byte vb.) varsa hatayi yakalar
            return "[ŞİFRESİ VEYA MÜHRÜ ÇÖZÜLEMEYEN VERİ]"

    def mathematical_handshake(self, is_host):
        # ddos/port tarama onlemi icin ag bazli dogrulama baslar
        self.log("Güvenlik doğrulama protokolü başlatıldı...", "SİSTEM")
        time.sleep(0.5) # ag gecikmesi onlemi
        
        try:
            if is_host:
                # 1 ile 50 arasinda rastgele bir challenge (sayi) uretir
                challenge = secrets.randbelow(50) + 1
                # challenge'i karsi tarafa gonderir
                self.conn.send(str(challenge).encode('utf-8'))
                # karsi taraftan gelecek olan response degerini (sayiyi) okur
                response = int(self.conn.recv(1024).decode('utf-8'))
                # formati (sayi * 2 + 7) olan beklenen matematiksel degeri hesaplar
                expected = (challenge * 2) + 7 
                
                # eger karsi tarafin yolladigi yanit, hesaplanan degere esitse
                if response == expected:
                    # tcp uzerinden OK sinyali gonderir
                    self.conn.send("OK".encode('utf-8')) 
                    self.log("Doğrulama başarılı.", "BAŞARILI")
                    return True # dogrulama basarili
                else:
                    # yanlis hesaplama yapildiysa REJECT sinyali gonderir
                    self.conn.send("REJECT".encode('utf-8')) 
                    self.log("Hatalı doğrulama! Bağlantı kesildi.", "HATA")
                    return False # baglanti reddedilir
            else:
                # host'tan gelen challenge degerini tcp agindan okur
                challenge = int(self.conn.recv(1024).decode('utf-8'))
                # onceden belirlenmis formati uygulayarak response degerini olusturur
                response = (challenge * 2) + 7  
                # response degerini host makineye iletir
                self.conn.send(str(response).encode('utf-8'))
                # host'un degerlendirmesi sonrasi atacagi karari (verdict) okur
                verdict = self.conn.recv(1024).decode('utf-8')
                
                # gelen karar OK ise
                if verdict == "OK":
                    self.log("Sunucu kimliği onayladı.", "BAŞARILI")
                    return True
                else:
                    # degilse erisim engellenmistir
                    self.log("Sunucu reddetti! Bağlantı kesiliyor.", "HATA")
                    return False
        except Exception as e:
            # baglanti kopmasi vb durumlari false ile yakalar
            return False

    def receive_messages(self):
        # thread icerisinde while true dongusuyle sonsuz bir ag dinlemesi baslatir
        while True:
            try:
                # soket tampon belleginden (buffer) max 4096 byte okur (bu satirda islemci bloklanir)
                data = self.conn.recv(4096)
                # eger okunan veri bossa, tcp baglantisi karsi tarafca kapatilmistir
                if not data:
                    break # donguden cikar
                
                # gelen raw byte veriyi utf-8 karakter formatina cevirir
                mesaj = data.decode('utf-8')
                # gelen veri ayirici karakter (|) ise programin kapanis sinyalidir
                if mesaj == "|":
                    self.log("Karşı taraf bağlantıyı kesti. Çıkmak için Enter'a basın.", "UYARI")
                    break # ag dinlemesini bitirir
                
                # debug amaciyla gelen ham base64 paketinin sadece bas kismini ekrana basar
                print(f"\n[AĞDAKİ HİBRİT PAKET] {mesaj[:45]}...") 
                # base64 formundaki mesaji desifreleme islemine sokar
                decrypted_mesaj = self.decrypt_message(mesaj)
                # cozulmus mesaji ekrana yonlendirir
                self.display_message("KARŞI TARAF", decrypted_mesaj)
            except:
                # recv komutunda kopma yaslanirsa donguyu bitirir
                break

    def chat_interface(self):
        # standart cli kullanici arayuzu metinleri (ui yazdirma islemleri)
        print("-" * 50)
        print("        SECURECHAT - E2EE CLI")
        print(f"        Rol: {self.role} | Durum: Şifreleme Aktif")
        print("-" * 50)
        self.log("Güvenli sohbet kanalına geçildi. Çıkış: '|'\n", "SİSTEM")

        # receive_messages fonksiyonunu ayri bir is parcacigina (thread) atar
        # daemon=True: ana program calismayi durdurdugunda bu thread'i de otomatik sonlandirir
        threading.Thread(target=self.receive_messages, daemon=True).start()

        # klavye (input) girislerini yakalamak icin ana thread dongusu
        while True:
            try:
                # tcp soketi acik mi (kapanmis mi) kontrolu
                if self.conn.fileno() == -1:
                    break # kapaliysa donguden cikar
                # input satiri thread'i bloklar, kullanici yazana kadar bekler (whitespaceler silinir)
                user_input = input("").strip()

                # kullanici cikis sinyali girerse
                if user_input == "|":
                    # karsi tarafa da kapanis sinyalini ag uzerinden gonderir
                    self.conn.send(user_input.encode('utf-8'))
                    time.sleep(0.5) # iletimin tamamlanmasi icin bekleme payi
                    break # input dongusunden cikar

                # hmac butunluk dogrulamasi testi
                if user_input == "!sabote":
                    # aes fonksiyonunu pas gecerek bilerek manlamsiz/hatali veri olusturur
                    fake_payload = "BozukVeri123/456+789==" 
                    # veriyi raw byte olarak agdan firlatir
                    self.conn.send(fake_payload.encode('utf-8'))
                    self.log("SİMÜLASYON: Ağa bozuk paket gönderildi.", "HACKER")
                    continue # input dongusunu bastan alir, sifrelemeye girmez

                # kullanici bos (enter) gecerse
                if not user_input:
                    continue # islemi atla, basa don

                # gonderilecek veriyi kullanicinin kendi ekraninda gosterir
                self.display_message("SEN", user_input)
                # user_input verisini aes ile sifreleme fonksiyonuna gonderir
                encrypted_payload = self.encrypt_message(user_input)
                # fonksiyon bos dondurmezse (sifreleme basariliysa)
                if encrypted_payload:
                    # sifreli base64 verisini tcp soketinden hedefe iletir
                    self.conn.send(encrypted_payload.encode('utf-8'))

            except:
                # klavye interrupt (ctrl+c) vb durumlari yonetir
                self.log("Bağlantı koptu. Menüye dönülüyor...", "UYARI")
                time.sleep(1) # terminal cikisi oncesi bekleme
                break
                
        # eger donguden cikilmissa (hata veya isteyerek) ve soket hala varsa
        if self.conn:
            # ag baglantisini isletim sistemi seviyesinde kapatir
            self.conn.close()

    def start_host(self):
        # kullanici rolunu set eder
        self.role = "HOST"
        self.log("Sunucu modunda başlatılıyor...", "SİSTEM")
        
        # ipv4 (AF_INET) formatinda tcp (SOCK_STREAM) soket objesi yaratir
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # kernel uzerindeki time_wait engeline takilmamak icin soketi yeniden kullanilabilir isaretler
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # belirtilen portu, butun ag arayuzlerinden (0.0.0.0) gelen trafik icin isletim sistemine kaydeder (bind)
        server.bind(('0.0.0.0', self.PORT)) 
        # porta gelen tcp baglanti isteklerini 1 kuyruk siniriyla (backlog) dinlemeye baslar
        server.listen(1)
        
        self.log(f"Kriptografik Modül Hazır. RSA-2048 aktif.", "KRİPTO")
        self.log(f"{self.PORT} portu dinleniyor...", "AĞ")
        
        # programi bu satirda dondurup tcp el sikismasi gelmesini bekler. basarili baglanti nesnesini (conn) ve ip/port adresini (addr) doner
        self.conn, addr = server.accept()
        self.log(f"Bağlantı yakalandı: {addr[0]}", "AĞ")
        time.sleep(0.5) # ag senkronizasyon molasi
        
        # mimari sira: 1. el sikisma (ddos korumasi)
        if self.mathematical_handshake(is_host=True):
            # 2. anahtar takasi (rsa-aes)
            if self.exchange_keys(is_host=True):
                # 3. cli terminalinin (sohbet arayuzu) baslatilmasi
                self.chat_interface()
            else:
                # takas basarisizsa soketi temizle
                self.conn.close()
        else:
            # el sikisma basarisizsa soketi kapat
            self.conn.close()
            # main menuye donmeden kullanici girdisi bekle
            input("\nMenüye dönmek için Enter'a basın...")

    def start_client(self):             
        # kullanici rolunu set eder
        self.role = "CLIENT"
        # ag hedefini (ip) standart text input ile alir
        ip = input("Bağlanılacak Host IP: ").strip() 
        
        # ipv4 formatinda tcp soket objesi yaratir
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log(f"{ip}:{self.PORT} adresine bağlanılıyor...", "AĞ")      
        
        try:
            # hedef ip ve porta tcp baglanti (syn) istegi firlatir
            self.conn.connect((ip, self.PORT))
            self.log("Sunucuya ulaşıldı. Doğrulama yapılıyor...", "AĞ")
            
            # mimari sira: 1. el sikisma (challenge response)
            if self.mathematical_handshake(is_host=False):
                # 2. rsa ile sifreli aes anahtar takasi
                if self.exchange_keys(is_host=False):
                    # 3. basarili baglanti sonrasi arayuz aktarimi
                    self.chat_interface()
                else:
                    self.conn.close()
            else:
                self.conn.close()
                input("\nMenüye dönmek için Enter'a basın...")
                
        except ConnectionRefusedError:
            # hedef pc kapali veya port dinlemiyorsa rst cevabi gelir, bu hata yakalanir
            self.log("Bağlantı reddedildi. Hedef makine açık mı?", "HATA")
            input("Menüye dönmek için Enter'a basın...")

    def run(self):
        # ana terminal menusunu donduren sonsuz dongu
        while True:
            # menuyu yazdirmadan once ekrani temizler
            self.clear_screen()
            # standart ui frame cizimleri
            print("┌──────────────────────────────────────────┐")
            print("│         SECURECHAT ANA MENÜ              │")
            print("├──────────────────────────────────────────┤")
            print("│  1. Ana Makine (Host) Ol                 │")
            print("│  2. İstemci (Client) Ol                  │")
            print("│  0. Çıkış                                │")
            print("└──────────────────────────────────────────┘")

            # klavyeden giris degeri alir
            choice = input("Seçim: ")

            # secim 1 ise host baslatma rutinine gider
            if choice == '1':
                self.start_host()
            # secim 2 ise client baslatma rutinine gider
            elif choice == '2':
                self.start_client()
            # secim 0 ise python processini os uzerinden tamamen kapatir
            elif choice == '0':
                sys.exit()

# python betigi dogrudan calistiriliyorsa (import edilmediyse) 
if __name__ == "__main__":
    # SecureChat sinifindan bir obje yaratir
    app = SecureChat()
    # objenin ana calistirma (run) metodunu tetikler
    app.run()