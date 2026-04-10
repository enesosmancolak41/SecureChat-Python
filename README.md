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
