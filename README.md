# SecureChat (Uçtan Uca Şifreli Mesajlaşma)

## Proje Hakkında
SecureChat, istemci-sunucu (client-server) mimarisine dayanan, komut satırı (CLI) üzerinden çalışan uçtan uca şifreli bir mesajlaşma uygulamasıdır. Bu proje, kriptoloji algoritmalarının pratik olarak uygulanmasını ve ağ üzerinden güvenli veri iletimini sağlamak amacıyla geliştirilmektedir.

## Gereksinim Analizi ve Araç Seçimi (Hafta 11 Raporu)

Bu projenin mimarisi tasarlanırken güvenlik, hız ve esneklik göz önüne alınarak aşağıdaki araçlar ve teknolojiler tercih edilmiştir:

* **Programlama Dili: Python 3.x**
    * **Neden Seçildi?** Siber güvenlik alanında sektör standardı olması, ağ programlama (`socket`) için sunduğu esnek yapı ve güçlü kriptografik kütüphane ekosistemi nedeniyle tercih edilmiştir. Ayrıca CLI tabanlı, stabil bir yapı kurmaya en uygun dildir.

* **Kriptografi Kütüphanesi: PyCryptodome**
    * **Neden Seçildi?** AES ve RSA gibi modern şifreleme algoritmalarını donanımsal olarak optimize edilmiş bir şekilde sunan güncel bir kütüphanedir. ECB gibi zayıf modlar yerine, projenin ilerleyen aşamalarında kullanılacak olan CBC veya GCM gibi güvenli şifreleme modlarının kolayca ve hatasız entegre edilmesine olanak tanır.

* **Ağ Haberleşmesi: Python `socket` Kütüphanesi**
    * **Neden Seçildi?** İki cihaz arasındaki TCP/IP haberleşmesini en temel ve kontrol edilebilir seviyede yönetmek için harici bir paket yerine Python'ın dahili soket kütüphanesi kullanılmıştır.

* **Rastgelelik (CSPRNG): Python `secrets` Kütüphanesi**
    * **Neden Seçildi?** Şifreleme işlemleri için gereken IV (Initialization Vector) üretimi ve Handshake (El Sıkışma) süreçlerinde kullanılacak rastgele sayıların tahmin edilemez olması hayati önem taşır. Bu nedenle standart `random` kütüphanesi yerine, kriptografik olarak güvenli sayılar üreten `secrets` modülü raporlanmış ve projeye dahil edilmiştir.

## Arayüz Kararı
Proje, arka planda çalışan matematiksel algoritmaların (şifreleme/çözme) ve ağ paketlerinin (Handshake, IV transferleri) anlık olarak izlenebilmesi, hata ayıklama süreçlerinin daha şeffaf yönetilebilmesi için **CLI (Komut Satırı Arayüzü)** olarak tasarlanmıştır.

## Algoritma Akış Şeması (Flowchart)

Aşağıdaki şema, iki kullanıcı (İstemci ve Sunucu) arasındaki bağlantı doğrulama (Handshake) ve ardından gerçekleşen uçtan uca şifreli mesajlaşma sürecini göstermektedir.

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
    Note over S: Orijinal mesaj alıcıya gösterilir

  ## HAFTA 13: AES-256 SİMETRİK ŞİFRELEME VE VERİ GİZLİLİĞİ

Bu aşamada, SecureChat uygulamasının ağ üzerinden ilettiği tüm veriler, kriptoloji dünyasının altın standardı kabul edilen **AES-256** algoritması ile uçtan uca şifrelenmiştir.

### 1. Teknik Mimari ve Algoritma Seçimi
Projenin gizlilik (Confidentiality) katmanında aşağıdaki teknik parametreler kullanılmıştır:

* **Algoritma:** AES (Advanced Encryption Standard)
* **Anahtar Uzunluğu:** 256 Bit (32 Byte) - `AES-256`
* **Blok Modu:** CBC (Cipher Block Chaining)
* **Doldurma (Padding):** PKCS7
* **Karakter Seti:** UTF-8 (Tam Türkçe karakter desteği)

### 2. Güvenlik Mekanizmaları

#### CBC Modu ve Dinamik IV
Statik şifreleme risklerini önlemek amacıyla **CBC (Cipher Block Chaining)** modu tercih edilmiştir. 
* Her mesaj gönderiminde `secrets` modülü kullanılarak eşsiz bir **IV (Initialization Vector)** üretilir.
* Bu sayede ağ üzerinden geçen paketler her seferinde farklı görünerek "Replay" ve "Frekans Analizi" saldırılarını engeller.

#### Base64 Kodlama
Şifrelenmiş ham byte verileri, ağ protokollerinde (TCP/IP) karakter bozulması yaşanmaması amacıyla **Base64** formatına dönüştürülerek iletilmektedir. Bu sayede veri bütünlüğü korunurken terminal ekranında "okunamaz çıktı" kriteri sağlanmaktadır.

---

### 3. DÖÇ 3 - Başarım ve Kanıt Tablosu

Hocanın değerlendirme kriterlerine (DÖÇ 3) göre hazırlanan teknik kanıtlar aşağıdadır:

| Kriter | Uygulanan Teknik | Kod İçindeki Karşılığı | Durum |
| :--- | :--- | :--- | :--- |
| **AES-256 Gücü** | 256 Bit Anahtar Yapısı | `AES.new(key, AES.MODE_CBC, iv)` | ✅ Başarılı |
| **Okunamaz Çıktı** | Ciphertext Üretimi | `[AĞDAN GELEN PAKET - BASE64]` | ✅ Başarılı |
| **Base64 Formatı** | Güvenli Veri Taşıma | `base64.b64encode(data)` | ✅ Başarılı |
| **Veri Güvenliği** | Rastgele IV Kullanımı | `secrets.token_bytes(16)` | ✅ Başarılı |

---

### 4. Örnek İletişim Çıktısı (Test Analizi)

Uygulama çalıştırıldığında ağ trafiğinin görünümü şu şekildedir:

> **Gönderilen Metin:** "Gizli operasyon başladı, 12345 portu güvende."
>
> **Ağdaki Görüntü (Base64):** `Oxvb7t2jqxyEKhp9szWb0qL11v9Uv/S1Wiju7Vu4iH5brW5u5NS8ODpxRM74h4pq...`
>
> **Alıcı Tarafı (Çözülmüş):** "Gizli operasyon başladı, 12345 portu güvende."

---

**NOT:** Bu rapor, projenin şifreleme fonksiyonlarının rubrikteki beklentileri tam olarak karşıladığını kanıtlamaktadır. Hafta 14 kapsamında, sabit anahtar yerine **RSA Asimetrik Şifreleme** ile anahtar değişimi entegre edilecektir.
