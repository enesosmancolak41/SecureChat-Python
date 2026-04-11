# SecureChat (Uçtan Uca Şifreli Mesajlaşma)

## Proje Hakkında
SecureChat, istemci-sunucu (client-server) mimarisine dayanan, komut satırı (CLI) üzerinden çalışan uçtan uca şifreli bir mesajlaşma uygulamasıdır. Bu proje, kriptoloji algoritmalarının pratik olarak uygulanmasını ve ağ üzerinden güvenli veri iletimini sağlamak amacıyla geliştirilmektedir.

## Gereksinim Analizi ve Araç Seçimi (Hafta 11 Raporu)

Bu projenin mimarisi tasarlanırken güvenlik, hız ve esneklik göz önüne alınarak aşağıdaki araçlar ve teknolojiler tercih edilmiştir:

* **Programlama Dili: Python 3.x**
    * **Neden Seçildi?** Siber güvenlik alanında sektör standardı olması, ağ programlama (`socket`) için sunduğu esnek yapı ve güçlü kriptografik kütüphane ekosistemi nedeniyle tercih edilmiştir. 

* **Kriptografi Kütüphanesi: PyCryptodome**
    * **Neden Seçildi?** AES ve RSA gibi modern şifreleme algoritmalarını donanımsal olarak optimize edilmiş bir şekilde sunan güncel bir kütüphanedir.

* **Ağ Haberleşmesi: Python `socket` Kütüphanesi**
    * **Neden Seçildi?** İki cihaz arasındaki TCP/IP haberleşmesini en temel ve kontrol edilebilir seviyede yönetmek için kullanılmıştır.

* **Rastgelelik (CSPRNG): Python `secrets` Kütüphanesi**
    * **Neden Seçildi?** Şifreleme işlemleri için gereken IV üretimi ve Handshake süreçlerinde kullanılacak rastgele sayıların tahmin edilemez olması hayati önem taşır.

## Algoritma Akış Şeması (Flowchart)

Aşağıdaki şema, bağlantı doğrulama (Handshake) ve ardından gerçekleşen uçtan uca şifreli mesajlaşma sürecini göstermektedir.

```mermaid
sequenceDiagram
    autonumber
    participant I as İstemci (Client)
    participant S as Sunucu (Server)

    Note over I,S: --- 1. AŞAMA: GÜVENLİ BAĞLANTI (HANDSHAKE) ---
    S->>I: Rastgele Sayı (Challenge) Gönderir
    Note over I: Gelen sayıyı gizli <br>matematiksel işleme sokar
    I->>S: İşlenmiş Cevabı Geri Gönderir
    
    alt Cevap Doğru
        S->>I: Bağlantı Onaylanır (Güvenli Bölge)
    else Cevap Yanlış
        S-->>I: Bağlantı Reddedilir! (Sistem Kapanır)
    end

    Note over I,S: --- 2. AŞAMA: ŞİFRELİ İLETİŞİM (AES-256) ---
    Note over I: Kullanıcı düz metin mesajı yazar
    Note over I: Mesaj AES-256 ile şifrelenir
    I->>S: Şifreli Veri (Base64) Ağdan İletilir
    Note over S: AES anahtarı ile şifre çözülür
    Note over S: Orijinal mesaj alıcıya gösterilir```


HAFTA 13: AES-256 SİMETRİK ŞİFRELEME VE VERİ GİZLİLİĞİBu aşamada, mesajlar ağ üzerinden geçmeden önce AES-256 algoritması ile zırhlanmıştır.1. Teknik ParametrelerAlgoritma: AES-256 (32 Byte Key)Blok Modu: CBC (Cipher Block Chaining)Doldurma: PKCS7 PaddingFormat: Base64 Encoding (Ağda güvenli taşıma için)2. Güvenlik AvantajlarıDinamik IV: secrets.token_bytes(16) ile her mesajda farklı bir IV üretilir. Bu sayede aynı mesajlar bile ağda farklı görünür.Gizlilik: Ağ trafiği dinlense dahi elde edilecek tek veri anlamsız bir Base64 yığınıdır.3. DÖÇ 3 - Başarım ve Kanıt TablosuKriterUygulanan TeknikKod KarşılığıDurumAES-256 Gücü256 Bit Anahtar YapısıAES.new(key, AES.MODE_CBC, iv)✅ BaşarılıOkunamaz ÇıktıCiphertext Üretimi[AĞDAN GELEN PAKET - BASE64]✅ BaşarılıBase64 FormatıGüvenli Veri Taşımabase64.b64encode(data)✅ Başarılı4. Örnek İletişim Çıktısı (Test Analizi)Gönderilen Metin: "Gizli operasyon başladı, 12345 portu güvende."Ağdaki Görüntü (Base64): Oxvb7t2jqxyEKhp9szWb0qL11v9Uv/S1Wiju7Vu4iH5brW5u5NS8ODpxRM74h4pq...Alıcı Tarafı (Çözülmüş): "Gizli operasyon başladı, 12345 portu güvende."
