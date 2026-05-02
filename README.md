🛡️ SecureChat: Uçtan Uca Şifreli (E2EE) CLI İletişim Protokolü
Geliştirici: Enes Osman Çolak - 23631039

Teknoloji Yığını: Python 3.10+, PyCryptodome, TCP/IPv4 Socket, Multi-threading

Mimari Sınıfı: Hibrit Kriptografi (Asymmetric Key Exchange + Symmetric Cipher + MAC)

1. Projenin Amacı ve Kapsamlı Tehdit Modeli (Threat Model)
Bu proje, güvenilmeyen ağ topolojilerinde (Ortak Wi-Fi, kampüs ağları, ISS seviyesindeki dinlemeler) iki uç birim (Host ve Client) arasındaki iletişimin Gizlilik (Confidentiality), Bütünlük (Integrity) ve Doğrulanabilirlik (Authentication) (CIA Triad) ilkelerini sağlamak amacıyla sıfırdan geliştirilmiş komut satırı (CLI) tabanlı bir haberleşme protokolüdür.

Sistem, ağ üzerinde gerçekleştirilebilecek aşağıdaki vektörlere karşı tam koruma sağlayacak şekilde dizayn edilmiştir:

Ağ Dinleme (Sniffing/Eavesdropping): Paketlerin Wireshark/tcpdump gibi araçlarla yakalanması durumuna karşı AES-256 şifrelemesi.

Ortadaki Adam (Man-in-the-Middle / ARP Spoofing): Araya giren saldırganın paketleri okumasını engellemek için RSA-2048 ile asimetrik anahtar takası.

Veri Manipülasyonu (Malleability/Bit-Flipping): Ağdaki şifreli paketlerin bit değerlerinin değiştirilerek anlamlı veya çökertici veri elde edilmesine karşı HMAC-SHA256 dijital mühürleme mekanizması.

Tekrar (Replay) Saldırıları: Aynı mesajın tekrar gönderilmesiyle ağ trafiğinin manipüle edilmesine karşı her pakette CSPRNG tabanlı benzersiz Başlangıç Vektörü (IV) kullanımı.

2. Kriptografik Mimari ve Teknik Analiz
Projenin çekirdeğini oluşturan kriptografik motor, simetrik ve asimetrik algoritmaların spesifik dezavantajlarını ortadan kaldıran üç katmanlı bir Hibrit Şifreleme mimarisinden oluşmaktadır.

2.1. Asimetrik Şifreleme ve Güvenli Anahtar Takası (RSA-2048 & PKCS#1 OAEP)
Simetrik şifreleme algoritmalarının en büyük handikapı olan "Anahtar Dağıtımı Zafiyeti" (Key Distribution Problem), sistemde RSA-2048 algoritması ile çözülmüştür. RSA'in işlemci maliyetinin yüksek olması nedeniyle bu algoritma veri şifrelemek için değil, yalnızca simetrik oturum anahtarını (Session Key) taşımak için kullanılmıştır.

Dinamik Anahtar Üretimi: Her iki cihaz (Host ve Client) TCP bağlantısı kurulduğu an bellekte (RAM) 2048-bit uzunluğunda birer Public/Private Key (Açık ve Gizli Anahtar) çifti üretir. Anahtarlar asla diske yazılmaz.

Key Exchange (Takas) Aşaması: Cihazlar Public Key'lerini X.509 PEM formatında birbirlerine düz metin olarak gönderir. Host makine, oturum boyunca veri akışını şifreleyecek olan 32-Byte'lık (256-bit) simetrik AES Session Key'i secrets.token_bytes() kullanarak donanımsal rastgelelikle üretir.

Zırhlı İletim ve OAEP Padding: AES Session Key, ağa kesinlikle çıplak bırakılmaz. İstemcinin Public Key'i kullanılarak RSA ile şifrelenir. Bu işlem sırasında klasik PKCS#1 v1.5 yerine, Padding Oracle saldırılarına karşı matematiksel olarak kanıtlanmış güvenliğe sahip PKCS1_OAEP (Optimal Asymmetric Encryption Padding) standardı kullanılmıştır. Sadece doğru Private Key'e sahip olan alıcı makine bu RSA bloğunu çözüp içindeki AES anahtarını elde edebilir.

2.2. Simetrik Şifreleme (AES-256 CBC Modu)
Veri akışının düşük gecikme (low-latency) ile hızlı ve güvenli olarak şifrelenmesi için donanım seviyesinde optimize edilmiş Gelişmiş Şifreleme Standardı (AES) tercih edilmiştir.

Anahtar Uzunluğu: Kuantum sonrası tehditler ve Brute-force (Kaba Kuvvet) saldırılarına karşı askeri/finansal standartlarda koruma sağlayan 256-bit (32 Byte) oturum anahtarı kullanılmıştır.

Güvenli Mod (CBC - Cipher Block Chaining): ECB (Electronic Codebook) modunun blok tekrarlama zafiyetine karşı, her bloğun bir önceki şifreli blok ile XOR işlemine tabi tutulduğu CBC modu kullanılmıştır. Bu sayede aynı "Merhaba" metni arka arkaya gönderilse dahi ağ üzerinde tamamen farklı byte dizileri olarak görünür.

CSPRNG ve Benzersiz IV (Initialization Vector): CBC modunun XOR zincirini başlatmak için her mesaj şifrelenmeden önce Python'un secrets kütüphanesi ile 16 Byte'lık entropisi yüksek, kriptografik olarak güvenli benzersiz bir IV üretilir.

Blok Tamamlama (PKCS#7 Padding): AES algoritması verileri 16 Byte'lık bloklar halinde işler. Gönderilen metin 16'nın katı değilse, eksik baytlar PKCS#7 standardına göre pad algoritması ile doldurulur ve alıcı tarafında unpad ile temizlenir.

2.3. Veri Bütünlüğü ve Mühürleme (HMAC-SHA256)
Modern kriptografide şifreleme (Encryption) veriyi gizler ancak değiştirilmesini (Malleability) tek başına engelleyemez. Saldırgan şifreyi çözemese bile ağdaki baytları rastgele değiştirerek sistemin çökmesine neden olabilir. Bu projede "Encrypt-then-MAC" (Önce Şifrele, Sonra Mühürle) paradigması uygulanmıştır.

Dijital Mühür Üretimi: Şifreleme işlemi tamamlandıktan sonra; şifreli veri (IV + Ciphertext) ve gizli AES Session Key kullanılarak Hash tabanlı bir Mesaj Doğrulama Kodu (HMAC) üretilir. Özet fonksiyonu olarak collision (çakışma) direnci yüksek olan SHA-256 kullanılmıştır ve pakete 32 Byte'lık bir imza (Signature/Digest) eklenmiştir.

Bütünlük Doğrulaması (Hash Kontrolü): Alıcı paketi ağdan okuduğunda veriyi AES motoruna sokmadan önce, kendi Session Key'i ile bu mührü yeniden hesaplar. Eğer yolda bir hacker paketin tek bir bitini bile manipüle etmişse (Bit-Flipping), hmac.verify() mekanizması anında ValueError istisnası fırlatır. Kod, şifreyi çözmeyi reddeder ve "❌ [GÜVENLİK İHLALİ] Bütünlük kontrolü başarısız!" uyarısı vererek bozuk paketi güvenli bir şekilde çöpe atar (Drop).

3. Ağ Mimarisi, Soket Programlama ve Paralel İşleme
3.1. TCP/IP İletişimi ve Port Yönetimi (Socket API)
Sistem, Taşıma Katmanında (Transport Layer) AF_INET (IPv4) adresleme ailesini ve paket sıralamasını/kayıpsız teslimatı garanti eden SOCK_STREAM (TCP) protokolünü kullanmaktadır.

Zombi Port Yönetimi: Olası istemci kopmaları, ağ çökmeleri veya programın ani kapatılması durumlarında işletim sisteminin 5555 numaralı portu "TIME_WAIT" durumunda rehin almasını engellemek için SO_REUSEADDR soket opsiyonu kernel seviyesinde aktifleştirilmiştir. Bu sayede "Address already in use" hatası donanımsal olarak bypass edilmiştir.

3.2. Asenkron İletişim (Multi-Threading)
Terminal tabanlı (CLI) standart I/O işlemlerinde input() fonksiyonu thread'i bloke ettiği (Blocking I/O) için "Full-Duplex" (Çift Yönlü Eşzamanlı İletişim) iletişim standart döngülerle sağlanamaz.

Bu darboğazı aşmak için Python'un threading kütüphanesi kullanılmıştır. Ağdan gelen paketleri dinleyen receive_messages fonksiyonu bağımsız bir Daemon Thread (Arka plan iş parçacığı) olarak izole edilmiştir. Bu asenkron mimari sayesinde kullanıcı klavyeden mesaj yazarken ağdan gelen mesajları gecikmesiz olarak ekranında görebilmektedir.

3.3. Erişim Güvenliği (Mathematical Challenge-Response Handshake)
Sistemin çalıştığı portun Nmap, Masscan gibi siber güvenlik zafiyet tarama araçları veya rastgele internet botları tarafından meşgul edilmesini/çökertilmesini engellemek için, asıl kriptografik takastan hemen önce uygulama katmanında (Application Layer) çalışan 3 adımlı özel bir matematiksel el sıkışma tasarlanmıştır.

Süreç: Bağlantı geldiğinde Host makine, istemciye donanımsal rastgelelikte bir Challenge (Soru) yollar. İstemci, kaynak kodda gömülü olan spesifik matematiksel formülü (challenge * 2) + 7 kullanarak Response (Cevap) üretmek zorundadır. Cevap doğrulanamazsa Host makine bir REJECT sinyali gönderir ve TCP soketini ağ seviyesinde acımasızca kapatır.

4. Veri Paketleme Formülasyonu (Payload Structure) ve Bayt Haritası
Ağ donanımlarının (Router, Switch, IDS/IPS), şifrelenmiş verilerdeki rastgele "Raw Byte" (Ham Hex) karakterlerini sistem kontrol komutu (EOF, Null Byte \x00 vb.) sanarak paketi parçalamasını veya drop etmesini önlemek amacıyla, taşıma katmanı yükü (Payload) Base64 algoritmasıyla sadece ASCII karakterlere kodlanmıştır. Türkçe karakter veri kayıplarını önlemek adına tüm dizi işlemleri uçtan uca UTF-8 Encoding standartlarına oturtulmuştur.

Ağa gönderilen tek bir veri paketinin bayt düzeyindeki yapısal anatomisi şöyledir:

Plaintext
Payload = Base64_Encode ( [16-Byte IV] + [N-Byte Ciphertext (PKCS7)] + [32-Byte HMAC_SHA256_Signature] )
Alıcı sistemi bu Base64 paketini deşifre ettiğinde diziyi sondan 32 bayt keserek HMAC imzasını ayırır, baştan 16 bayt keserek IV'yi alır ve ortada kalan gövdeyi AES motoruna deşifre (Decryption) işlemi için iletir.

5. Sonuç ve Güvenlik Senaryoları Değerlendirmesi
Mimarisi açıklanan bu uçtan uca şifreli protokol üzerinde gerçekleştirilen stres ve sızma testlerinin sonuçları aşağıdadır:

Ağ Dinleme (Sniffing) Testi - Wireshark: Ağ trafiği izlendiğinde, el sıkışma aşamasındaki RSA takasları dışında sadece Base64 ile kodlanmış anlamsız veri blokları gözlemlenmiştir. Paketlerin içeriklerine veya simetrik oturum anahtarına dair hiçbir entropi sızıntısı tespit edilmemiştir.

Veri Manipülasyonu (Sabotaj / Malleability) Testi: Koda entegre edilen simülasyon argümanı (!sabote) ile AES motoru bypass edilerek ağa sahte ve baytları değiştirilmiş geçersiz bir şifreli metin bırakılmıştır. Alıcı tarafındaki HMAC-SHA256 katmanı bu Ortadaki Adam manipülasyonunu mikrosaniyeler içinde tespit etmiş ve şifreyi çözmeyi reddederek sistemi güvende tutmuştur.

Kalıcı Anahtar Güvenliği (Forward Secrecy Temelleri): Tüm RSA anahtar çiftlerinin ve AES oturum anahtarlarının her bağlantı başlangıcında statik disk alanı yerine uçucu bellekte (RAM) dinamik olarak üretilmesi sayesinde, olası bir fiziksel makine ele geçirilmesi durumunda dahi geçmiş sohbet verilerinin anahtarlarına ulaşılması imkansız hale getirilmiş, proje E2EE (End-to-End Encryption) prensipleriyle tam uyumlu çalıştırılmıştır.

sequenceDiagram
    participant A as Gönderici (İstemci)
    participant N as Güvenli Olmayan Ağ
    participant B as Alıcı (İstemci/Sunucu)

    Note over A,B: 1. AŞAMA: RSA ANAHTAR DEĞİŞİMİ
    B-->>N: RSA Public Key (2048-bit) yayınla
    N-->>A: RSA Public Key'i ilet

    Note over A,B: 2. AŞAMA: OTURUM HAZIRLIĞI & ŞİFRELEME
    A->>A: 1. AES-256 Session Key üret (Rastgele)
    A->>A: 2. Mesajın SHA-256 Hash'ini al (Bütünlük)
    A->>A: 3. Mesajı AES-CBC + PKCS7 ile şifrele
    A->>A: 4. AES Key'i RSA-OAEP ile şifrele (Zırhlama)

    Note over A,B: 3. AŞAMA: VERİ İLETİMİ
    A->>N: [Şifreli AES Key] + [Şifreli Mesaj + Hash]
    N->>B: Paketi teslim et

    Note over A,B: 4. AŞAMA: DEŞİFRELEME & DOĞRULAMA
    B->>B: 1. RSA Private Key ile AES Key'i çöz
    B->>B: 2. AES Key ile Mesajı + Hash'i deşifre et (PKCS7 Unpad)
    B->>B: 3. Alınan mesajın tekrar Hash'ini hesapla
    B->>B: 4. Hash'leri Karşılaştır (SHA-256 Check)

    rect rgb(200, 255, 200)
    Note right of B: Doğrulama Başarılı: Mesaj Güvenli!
    end
