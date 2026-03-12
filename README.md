#  Notlarsende — Yapay Zekâ Destekli Not Paylaşım Platformu

> Öğrenciler arasındaki not paylaşımını dijitalleştiren, yapay zekâ desteğiyle kişiselleştirilmiş bir akademik alışveriş deneyimi sunan yenilikçi platform.

---

##  Proje Hakkında

**Notlarsende**, geleneksel not paylaşım yöntemlerinin ötesine geçerek öğrencilerin ders notlarını güvenli bir şekilde satışa sunabileceği, ihtiyaç sahiplerinin ise aradığı içeriğe yapay zekâ analizi ve sınıflandırmasıyla hızla ulaşabileceği bir ekosistem sunar.

Platform, kullanıcıların akademik materyallere erişimini kolaylaştırırken bilgi paylaşımı yoluyla gelir elde etmelerine de olanak sağlar.

---

## Özellikler

| Özellik | Açıklama |
|---|---|
| **Yapay Zekâ Motoru** | Notların otomatik sınıflandırılması, analizi ve kullanıcı ilgi alanlarına göre kişiselleştirilmiş geri bildirim |
|  **Zafer Chatbot** | Kullanıcı sorularını yanıtlayan, notları özetleyebilen ve geçmiş konuşmaları kaydeden dinamik AI asistanı |
|  **Donanım Arşivi** | İşlemlerin UTC formatında saklanıp yerel saatle gösterildiği şeffaf işlem geçmişi (Zaman Damgası) |
|  **Modüler Dosya Yönetimi** | Her kullanıcıya özel JSON tabanlı sepet ve yükleme klasörleri ile optimize edilmiş veri erişimi |
|  **Kullanıcı Paneli** | Satın alım geçmişi, ürün yönetimi ve profil düzenleme özelliklerini içeren kapsamlı hesap yönetimi |

---

##  Teknik Mimari

Sistem, sürdürülebilirlik ve performans için modüler bir yapıda tasarlanmıştır.

### Backend

- **Framework:** Python Flask
- **Veri Yönetimi:** JSON tabanlı yerel veritabanı *(Kullanıcılar, Ürünler, Sepetler, Destek Talepleri)*
- **Güvenlik:** E-posta/şifre doğrulaması (Regex), güvenli dosya adı işlemleri (`secure_filename`), UUID ile benzersiz ürün kimlikleri
- **Şablon Motoru:** Jinja2 *(Bileşen tabanlı `include` yapısı ile kod tekrarı önlenmiştir)*

### Frontend

- **Teknolojiler:** HTML5, CSS3, JavaScript (AJAX / FormData)
- **Tasarım:** TailwindCSS ve Bootstrap destekli, modern ve responsive (mobil uyumlu) UI/UX
- **Deneyim:** Sayfa yükleme hızını hissettiren Preloader ve asenkron (sayfa yenilenmeden) ürün yükleme süreçleri

---

##  Başarı Kriterleri

- Yapay zekâ sınıflandırmasında **%80 doğruluk oranı**
- Sistem kullanılabilirliğinde **%99 süreklilik**
- Güvenli giriş/çıkış sistemi ile **sıfır güvenlik açığı** hedefi

---

##  Proje Ekibi

| İsim |
|---|
| Orkun Bilgekağan Yakar |
| Şafak Kaçmaz |
| Ataberk Emre |
| Uygar Görmez |

---

##  Lisans

Bu proje akademik amaçlarla geliştirilmiştir.
