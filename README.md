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
    Note over S: Orijinal mesaj alıcıya gösterilir
