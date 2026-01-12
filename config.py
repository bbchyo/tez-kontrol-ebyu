# -*- coding: utf-8 -*-
"""
EBYÜ Tez Formatlama Kontrolcüsü - Konfigürasyon (v3)

EBYÜ Sosyal Bilimler Enstitüsü 2022 Tez Yazım Kılavuzu kuralları.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ErrorCategory(Enum):
    """Hata kategorileri"""
    MARGIN = "Kenar Boşluğu Hataları"
    FONT = "Yazı Tipi Hataları"
    FONT_SIZE = "Yazı Boyutu Hataları"
    LINE_SPACING = "Satır Aralığı Hataları"
    PARAGRAPH = "Paragraf Hataları"
    HEADING = "Başlık Hataları"
    TABLE = "Tablo Hataları"
    FIGURE = "Şekil Hataları"
    ABSTRACT = "Özet Hataları"
    REFERENCE = "Kaynakça Hataları"
    SECTION = "Bölüm Hataları"
    NUMBERING = "Numaralandırma Hataları"
    SPELLING = "Yazım Hataları"
    FOOTNOTE = "Dipnot Hataları"


@dataclass
class FormatError:
    """Format hatası"""
    category: ErrorCategory
    message: str
    location: str
    expected: str = ""
    found: str = ""
    snippet: str = ""
    severity: str = "error"


@dataclass
class ThesisConfig:
    """
    EBYÜ 2022 Tez Yazım Kılavuzu kuralları
    """
    
    # === SAYFA DÜZENİ ===
    # "Sayfanın tüm kenarlarından 3'er cm boşluk bırakılmalıdır"
    margin_top: float = 3.0
    margin_bottom: float = 3.0
    margin_left: float = 3.0
    margin_right: float = 3.0
    
    # "Ana bölüm başlıklarını içeren sayfalarda üstten 7 cm boşluk"
    chapter_start_margin_top: float = 7.0
    
    # Toleranslar
    margin_tolerance_cm: float = 0.1
    font_size_tolerance_pt: float = 0.5
    
    # === YAZI ÖZELLİKLERİ ===
    # "Tezin tüm metni Times New Roman yazı tipi kullanılarak 12 punto"
    font_name: str = "Times New Roman"
    font_size_body: int = 12
    
    # "Dipnotlar, Times New Roman yazı tipi kullanılarak 10 punto"
    font_size_footnote: int = 10
    
    # Blok Alıntı (40+ kelime, Her iki yandan 1.25cm girintili, 11 punto, İtalik)
    font_size_block_quote: int = 11
    block_quote_indent_cm: float = 1.25
    
    # "Bölüm başlıkları 14 punto, koyu ve ortalı"
    font_size_chapter_heading: int = 14
    
    # "Ana başlıklar ve alt başlıklar koyu, 12 punto"
    font_size_subheading: int = 12
    
    # "Tablo ve şekil başlıkları 12 punto, içindeki açıklamalar 11 punto"
    font_size_table_caption: int = 12
    font_size_figure_caption: int = 12
    font_size_table_content: int = 11
    
    # "Sayfa numaraları 10 punto"
    font_size_page_number: int = 10
    
    # Kapak sayfası boyutları
    font_size_cover_main: int = 16
    font_size_cover_support: int = 12
    font_size_cover_program: int = 14
    
    # === SATIR ARALIĞI ===
    # "Metin 1,5 satır aralıklı"
    line_spacing_body: float = 1.5
    
    # "Dipnotlar, şekil altı ve tabloların açıklamaları 1 satır aralıklı"
    line_spacing_footnote: float = 1.0
    line_spacing_table: float = 1.0
    line_spacing_figure: float = 1.0
    
    # === PARAGRAF ===
    # "Paragrafın ilk satırında 1,25 cm girinti"
    paragraph_first_line_indent: float = 1.25
    
    # "Paragraf aralıkları başlıklarda ve metin içinde önce 6 nk sonra 6 nk"
    paragraph_spacing_before: int = 6
    paragraph_spacing_after: int = 6
    
    # "Dipnotlarda önce 0 nk sonra 0 nk"
    paragraph_spacing_footnote_before: int = 0
    paragraph_spacing_footnote_after: int = 0
    
    # "Kaynakçada önce 3 nk sonra 3 nk"
    paragraph_spacing_reference_before: int = 3
    paragraph_spacing_reference_after: int = 3
    
    # === KAYNAKÇA ===
    # "Her kaynağın ilk satırı asılı 1 cm girintili"
    reference_hanging_indent: float = 1.0
    
    # === ÖZET ===
    # "Özet metni en az 200 en fazla 250 kelimeden oluşmalı"
    abstract_min_words: int = 200
    abstract_max_words: int = 250
    
    # "En az 3, en fazla 5 anahtar kelime"
    keywords_min: int = 3
    keywords_max: int = 5
    
    # === TEZ UZUNLUĞU ===
    # "Yüksek lisans en az 50 sayfa, doktora en az 80 sayfa"
    min_pages_masters: int = 50
    min_pages_doctoral: int = 80
    max_pages_single_volume: int = 500
    
    # === GEREKLI BÖLÜMLER ===
    required_sections: List[str] = field(default_factory=lambda: [
        "Özet",
        "Abstract",
        "İçindekiler",
        "Giriş",
        "Sonuç",
        "Kaynakça"
    ])
    
    # Opsiyonel bölümler
    optional_sections: List[str] = field(default_factory=lambda: [
        "Ön Söz",
        "Simgeler ve Kısaltmalar Listesi",
        "Tablolar Listesi",
        "Şekiller Listesi",
        "Ekler",
        "Özgeçmiş"
    ])


# Varsayılan konfigürasyon
DEFAULT_CONFIG = ThesisConfig()
