import time

def ekranı_temizle():
    # Terminal ekranını temizlemek için küçük bir hile
    print("\033[H\033[J", end="")

def ana_menu():
    ekranı_temizle()
    print("="*50)
    print(" "*10 + "SECURECHAT v1.0 - CLI Arayüzü")
    print("="*50)
    print(" [1] Bağlantı Bekle (Server Modu)")
    print(" [2] Birine Bağlan (Client Modu)")
    print(" [3] Çıkış")
    print("="*50)

    secim = input("\nLütfen bir işlem seçin (1/2/3): ")
    
    if secim == '1':
        print("\n[*] Gelen bağlantılar dinleniyor... (Henüz kodlanmadı)")
    elif secim == '2':
        ip_adres = input("[>] Bağlanılacak IP adresini girin: ")
        print(f"\n[*] {ip_adres} adresine bağlanılıyor... (Henüz kodlanmadı)")
    elif secim == '3':
        print("\nÇıkış yapılıyor...")
        time.sleep(1)
        exit()
    else:
        print("\n[!] Hatalı seçim, lütfen tekrar deneyin.")

if __name__ == "__main__":
    ana_menu()