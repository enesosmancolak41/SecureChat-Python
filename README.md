# 🛡️ SecureChat: Uçtan Uca Şifreli Mesajlaşma Sistemi

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![PyCryptodome](https://img.shields.io/badge/Library-PyCryptodome-green?style=for-the-badge&logo=lock)
![Status](https://img.shields.io/badge/Hafta-11%20Tamamland%C4%B1-success?style=for-the-badge)

SecureChat, iki makine arasında (Host-VM) yüksek güvenlikli, uçtan uca şifreli (E2EE) iletişimi sağlamak amacıyla geliştirilmiş bir kriptoloji projesidir.

---

## 📅 11. HAFTA: PLANLAMA, ANALİZ VE ARAYÜZ (15 PUAN)

Bu hafta projenin temelleri atılmış, teknoloji yığını belirlenmiş ve algoritma akış şeması oluşturulmuştur.

### 🛠️ 1. Gereksinim Analizi ve Araç Seçimi
Projenin rubrik şartlarını tam karşılaması için seçilen temel bileşenler:

| Bileşen | Seçilen Araç | Gerekçe |
| :--- | :--- | :--- |
| **Dil** | Python 3.x | Socket yönetimi ve zengin kripto kütüphaneleri. |
| **Kütüphane** | PyCryptodome | AES-256 ve RSA standartlarına tam uyum. |
| **Ağ Protokolü** | TCP Socket | Veri paketlerinin sırasının ve bütünlüğünün korunması. |
| **Arayüz** | CLI (Komut Satırı) | basit , hızlı ve modüler yapı. |

---

### 📊 2. Algoritma Akış Şeması (Flowchart)
Mesajın göndericiden alıcıya ulaşana kadar izlediği yol aşağıdaki diyagramda şematize edilmiştir:

```mermaid
graph TD
    A[Kullanıcı Mesaj Girişi] --> B{Şifreleme Süreci}
    B -->|AES-256| C[Şifreli Veri / Ciphertext]
    C --> D[TCP Socket Üzerinden İletim]
    D --> E[Alıcı Tarafı: Paket Karşılama]
    E --> F{Şifre Çözme Süreci}
    F -->|AES-256| G[Orijinal Mesajın Görüntülenmesi]
    
    style B fill:#f9f,stroke:#333,stroke-width:2px
    style F fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
