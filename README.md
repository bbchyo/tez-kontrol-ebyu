# EBYÜ Tez Format Kontrolcüsü

Erzincan Binali Yıldırım Üniversitesi Sosyal Bilimler Enstitüsü **2022 Tez Yazım Kılavuzu**'na göre tez formatı kontrol programı. bbc

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📋 Özellikler

Bu program Word (.docx) formatındaki tez dosyalarını analiz ederek format hatalarını tespit eder:

### Kontrol Edilen Parametreler

| Parametre | Kural | Kontrol |
|-----------|-------|---------|
| **Yazı Tipi** | Times New Roman | ✅ |
| **Metin Boyutu** | 12 punto | ✅ |
| **Bölüm Başlığı** | 14pt, koyu, ortalı, BÜYÜK HARF | ✅ |
| **Alt Başlık** | 12pt, koyu, 1.25cm girinti | ✅ |
| **Dipnot** | 10 punto | ✅ |
| **Blok Alıntı** | 11pt, italik, 1.25cm girinti | ✅ |
| **Satır Aralığı** | 1.5 (metin), 1.0 (dipnot/tablo) | ✅ |
| **Kenar Boşlukları** | 3cm (tüm kenarlar) | ✅ |
| **Paragraf Girintisi** | 1.25cm ilk satır | ✅ |
| **Paragraf Aralığı** | 6nk önce/sonra | ✅ |
| **Tablo/Şekil Numaralandırma** | X.Y formatı | ✅ |
| **Kaynakça** | 1cm asılı girinti, 3nk aralık | ✅ |
| **Özet** | 200-250 kelime | ✅ |
| **Sayfa Numarası** | 10pt, ortalı | ✅ |

## 🚀 Kurulum

```bash
# Repoyu klonla
git clone https://github.com/KULLANICI_ADI/tez-kontrol-ebyu.git
cd tez-kontrol-ebyu

# Sanal ortam oluştur
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

## 💻 Kullanım

### Web Arayüzü (Streamlit)

```bash
streamlit run app.py
```

Tarayıcınızda `http://localhost:8501` adresine gidin ve .docx dosyanızı yükleyin.

### Programatik Kullanım

```python
from checker import analyze_thesis
from config import ThesisConfig

# Varsayılan ayarlarla analiz
results = analyze_thesis("tez.docx")

print(f"Uyumluluk: %{results['compliance_score']}")
print(f"Toplam Hata: {results['total_errors']}")

# Hata detayları
for category, errors in results['grouped_errors'].items():
    print(f"\n{category}:")
    for err in errors:
        print(f"  - {err['location']}: {err['issues']}")
```

## 📁 Dosya Yapısı

```
tez-kontrol-ebyu/
├── app.py              # Streamlit web arayüzü
├── checker.py          # Ana analiz motoru
├── config.py           # Konfigürasyon ve kurallar
├── utils.py            # Yardımcı fonksiyonlar
├── requirements.txt    # Python bağımlılıkları
└── README.md
```

## ⚙️ Konfigürasyon

`config.py` dosyasından tüm parametreleri özelleştirebilirsiniz:

```python
from config import ThesisConfig

config = ThesisConfig(
    margin_top=3.0,           # Üst kenar boşluğu (cm)
    margin_bottom=3.0,        # Alt kenar boşluğu (cm)
    font_size_body=12,        # Metin boyutu (pt)
    line_spacing_body=1.5,    # Satır aralığı
    abstract_min_words=200,   # Özet minimum kelime
    abstract_max_words=250,   # Özet maksimum kelime
)

results = analyze_thesis("tez.docx", config)
```

## 📊 Örnek Çıktı

```
============================================================
EBYÜ TEZ FORMAT KONTROL RAPORU
============================================================
Uyumluluk Skoru: %97.7
Toplam Hata: 336
Bulunan Bölümler: 6/6

Hata Dağılımı:
  Paragraf Hataları:    138
  Yazı Boyutu:          114
  Tablo Hataları:        20
  Satır Aralığı:          9
  Başlık Hataları:        3
============================================================
```

## 🔧 Gereksinimler

- Python 3.9+
- python-docx
- streamlit
- zemberek-python (Türkçe yazım denetimi için)

## 📝 Lisans

MIT License - Serbestçe kullanabilir, değiştirebilir ve dağıtabilirsiniz.

## 🙏 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request açın

## 📚 Referans

Bu program [EBYÜ Sosyal Bilimler Enstitüsü 2022 Tez Yazım Kılavuzu](https://sbe.ebyu.edu.tr/) kurallarına göre geliştirilmiştir.

---

**Not:** Bu program resmi bir EBYÜ ürünü değildir. Tez tesliminden önce danışmanınızla kontrol edin.
