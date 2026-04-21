import os
import sys
from datetime import datetime
import time

class SecureChat:
    def __init__(self):
        self.role = None  # Kullanıcının rolü (HOST veya CLIENT)

    def clear_screen(self):
        """Terminal ekranını işletim sistemine uygun şekilde temizler."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message, log_type="INFO"):
        """Sistem uyarılarını zaman damgası ve etiket ile loglar."""
        time_str = datetime.now().strftime("%H:%M:%S")
        print(f"[{time_str}] [{log_type}] {message}")

    def display_message(self, sender, text):
        """Sohbet mesajlarını ekrana formatlı olarak basar."""
        time_str = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{time_str}] {sender} >> {text}")

    def chat_interface(self):
        """Mesajlaşma arayüzü ve simülasyon döngüsü."""
        self.clear_screen()
        print("="*60)
        print("        SECURECHAT - END-TO-END ENCRYPTED CLI v1.0")
        print(f"        Mod: {self.role} | Durum: Arayüz Tasarım Aşaması")
        print("="*60)

        self.log(f"{self.role} arayüzü başlatıldı.", "SİSTEM")
        self.log("Ağ bağlantısı aranıyor... (Simülasyon)", "AĞ")
        time.sleep(2)
        self.log("Karşı taraf bağlandı! (Simülasyon)", "BAŞARILI")
        self.log("İletişimi kesmek ve menüye dönmek için '|' kullanın.\n", "YARDIM")
        print("-" * 60)

        # Mesajlaşma döngüsü
        while True:
            try:
                user_input = input(f"[{self.role}] Mesajınız: ").strip()

                if user_input == "|":
                    self.log("Çıkış komutu algılandı. Ana menüye dönülüyor...", "SİSTEM")
                    time.sleep(2)
                    break  # Döngüyü kırıp ana menüye (run fonksiyonuna) geri döner

                if not user_input:
                    continue  # Boş enter basılırsa pas geç

                self.display_message("SEN", user_input)
                self.log("Ağ üzerinden gönderildi. (Simülasyon)\n", "İLETİM")

            except KeyboardInterrupt:
                self.log("Zorunlu çıkış yapıldı. Ana menüye dönülüyor...", "UYARI")
                time.sleep(1)
                break

    def run(self):
        """Kullanıcıyı karşılayan ana menü döngüsü."""
        while True:
            self.clear_screen()
            print("┌──────────────────────────────────────────┐")
            print("│         SECURECHAT ANA MENÜ              │")
            print("├──────────────────────────────────────────┤")
            print("│  1. Ana Makine (Host) Ol                 │")
            print("│  2. İstemci (Client) Ol                  │")
            print("│  0. Uygulamayı Kapat                     │")
            print("└──────────────────────────────────────────┘")

            choice = input("Lütfen seçiminizi yapın: ")

            if choice == '1':
                self.role = "HOST"
                self.chat_interface()
            elif choice == '2':
                self.role = "CLIENT"
                self.chat_interface()
            elif choice == '0':
                print("Güvenli çıkış yapıldı.")
                sys.exit()
            else:
                input("Hatalı seçim! Menüye dönmek için Enter'a basın...")

if __name__ == "__main__":
    app = SecureChat()
    app.run()