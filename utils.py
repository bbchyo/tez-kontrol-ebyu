# -*- coding: utf-8 -*-
"""
EBYÜ Tez Formatlama Kontrolcüsü - Yardımcı Fonksiyonlar

Bu modül birim dönüşümleri, regex desenleri ve diğer yardımcı fonksiyonları içerir.
"""

import re
from typing import Optional, Tuple, List, Any, Dict
from docx.shared import Pt, Cm, Emu, Twips
from docx.oxml.ns import qn
from docx.enum.text import WD_LINE_SPACING


# === BİRİM DÖNÜŞÜM SABİTLERİ ===
EMU_PER_CM = 360000  # 1 cm = 360000 EMU
EMU_PER_INCH = 914400  # 1 inch = 914400 EMU
EMU_PER_PT = 12700  # 1 pt = 12700 EMU
TWIPS_PER_CM = 567  # 1 cm ≈ 567 twips
TWIPS_PER_PT = 20  # 1 pt = 20 twips
PT_PER_INCH = 72  # 1 inch = 72 pt


def emu_to_cm(emu: Optional[int]) -> Optional[float]:
    """
    EMU (English Metric Units) değerini santimetreye çevirir.
    
    Args:
        emu: EMU cinsinden değer (None olabilir)
    
    Returns:
        Santimetre cinsinden değer veya None
    """
    if emu is None:
        return None
    return round(emu / EMU_PER_CM, 2)


def cm_to_emu(cm: float) -> int:
    """
    Santimetre değerini EMU'ya çevirir.
    
    Args:
        cm: Santimetre cinsinden değer
    
    Returns:
        EMU cinsinden değer
    """
    return int(cm * EMU_PER_CM)


def emu_to_pt(emu: Optional[int]) -> Optional[float]:
    """
    EMU değerini puntoya çevirir.
    
    Args:
        emu: EMU cinsinden değer
    
    Returns:
        Punto cinsinden değer veya None
    """
    if emu is None:
        return None
    return round(emu / EMU_PER_PT, 1)


def pt_to_emu(pt: float) -> int:
    """
    Punto değerini EMU'ya çevirir.
    
    Args:
        pt: Punto cinsinden değer
    
    Returns:
        EMU cinsinden değer
    """
    return int(pt * EMU_PER_PT)


def twips_to_cm(twips: Optional[int]) -> Optional[float]:
    """
    Twips değerini santimetreye çevirir.
    
    Args:
        twips: Twips cinsinden değer
    
    Returns:
        Santimetre cinsinden değer veya None
    """
    if twips is None:
        return None
    return round(twips / TWIPS_PER_CM, 2)


def cm_to_twips(cm: float) -> int:
    """
    Santimetre değerini twips'e çevirir.
    
    Args:
        cm: Santimetre cinsinden değer
    
    Returns:
        Twips cinsinden değer
    """
    return int(cm * TWIPS_PER_CM)


def twips_to_pt(twips: Optional[int]) -> Optional[float]:
    """
    Twips değerini puntoya çevirir.
    
    Args:
        twips: Twips cinsinden değer
    
    Returns:
        Punto cinsinden değer veya None
    """
    if twips is None:
        return None
    return round(twips / TWIPS_PER_PT, 1)


def pt_to_twips(pt: float) -> int:
    """
    Punto değerini twips'e çevirir.
    
    Args:
        pt: Punto cinsinden değer
    
    Returns:
        Twips cinsinden değer
    """
    return int(pt * TWIPS_PER_PT)



class StyleResolver:
    """
    Word dökümanlarındaki stil kalıtımını (inheritance) çözen yardımcı sınıf.
    """
    def __init__(self, doc):
        self.doc = doc
        self.styles = doc.styles
        self.doc_defaults = self._get_doc_defaults()

    def _get_doc_defaults(self) -> Dict[str, Any]:
        """Döküman varsayılanlarını (docDefaults) ayıklar."""
        defaults = {
            "font_name": None, 
            "font_size": None,
            "line_spacing": None,
            "line_spacing_rule": None,
            "space_before": None,
            "space_after": None,
            "alignment": None
        }
        try:
            # Font varsayılanları (rPrDefault)
            rPr_def = self.styles.element.xpath('w:docDefaults/w:rPrDefault/w:rPr')
            if rPr_def:
                rPr = rPr_def[0]
                # Yazı tipi
                rFonts = rPr.find(qn('w:rFonts'))
                if rFonts is not None:
                    defaults["font_name"] = rFonts.get(qn('w:ascii')) or rFonts.get(qn('w:hAnsi'))
                # Yazı boyutu
                sz = rPr.find(qn('w:sz'))
                if sz is not None:
                    defaults["font_size"] = int(sz.get(qn('w:val'))) / 2.0

            # Paragraf varsayılanları (pPrDefault)
            pPr_def = self.styles.element.xpath('w:docDefaults/w:pPrDefault/w:pPr')
            if pPr_def:
                pPr = pPr_def[0]
                # Boşluklar
                spacing = pPr.find(qn('w:spacing'))
                if spacing is not None:
                    before = spacing.get(qn('w:before'))
                    after = spacing.get(qn('w:after'))
                    line = spacing.get(qn('w:line'))
                    rule = spacing.get(qn('w:lineRule'))
                    
                    if before: defaults["space_before"] = int(before)
                    if after: defaults["space_after"] = int(after)
                    if line: defaults["line_spacing"] = int(line)
                    if rule: defaults["line_spacing_rule"] = rule
                
                # Hizalama
                jc = pPr.find(qn('w:jc'))
                if jc is not None:
                    defaults["alignment"] = jc.get(qn('w:val'))
        except Exception:
            pass
        return defaults

    def get_effective_font_name(self, run) -> str:
        """Run için geçerli yazı tipini bulur."""
        # 1. Manuel Formatlama
        if run.font.name:
            return run.font.name
        
        # XML kontrolü (Tema vs.)
        rPr = run._element.find(qn('w:rPr'))
        if rPr is not None:
            rFonts = rPr.find(qn('w:rFonts'))
            if rFonts is not None:
                font = rFonts.get(qn('w:ascii')) or rFonts.get(qn('w:hAnsi'))
                if font: return font
                
                # Tema Fontları
                theme = rFonts.get(qn('w:asciiTheme')) or rFonts.get(qn('w:hAnsiTheme'))
                if theme:
                    # EBYÜ: Theme fontları genellikle TNR veya Calibri'dir.
                    # Eğer döküman TNR üzerine kuruluysa theme fontları TNR olabilir.
                    # Ancak tespiti zor olduğundan, eğer theme varsa ve name yoksa
                    # 'Times' kelimesini arayalım.
                    if "minor" in theme: return "Times New Roman" # Çoğu akademik şablonda minor TNR'dır
                    return f"Tema ({theme})"

        # 2. Paragraf Stili ve Kalıtım
        style = run._parent.style if hasattr(run._parent, 'style') else None
        while style:
            if hasattr(style, 'font') and style.font.name:
                return style.font.name
            style = style.base_style
            
        # 3. Döküman Varsayılanları
        return self.doc_defaults.get("font_name") or "Calibri"

    def get_effective_font_size(self, run) -> Optional[float]:
        """Run için geçerli yazı boyutunu bulur."""
        # 1. Manuel Formatlama
        if run.font.size:
            return run.font.size.pt
            
        # XML kontrolü
        rPr = run._element.find(qn('w:rPr'))
        if rPr is not None:
            sz = rPr.find(qn('w:sz'))
            if sz is not None:
                return int(sz.get(qn('w:val'))) / 2.0

        # 2. Paragraf Stili ve Kalıtım
        style = run._parent.style if hasattr(run._parent, 'style') else None
        while style:
            if hasattr(style, 'font') and style.font.size:
                return style.font.size.pt
            style = style.base_style
            
        # 3. Döküman Varsayılanları
        return self.doc_defaults.get("font_size") or 11.0

    def get_effective_paragraph_attribute(self, paragraph, attr_name: str) -> Any:
        """Paragraf özelliği için kalıtımı çözer (space_before, alignment vb.)"""
        # 1. Manuel Formatlama (Direct formatting)
        pf = paragraph.paragraph_format
        val = getattr(pf, attr_name)
        if val is not None:
            return val

        # 2. Stil ve Kalıtım
        style = paragraph.style
        while style:
            if hasattr(style, 'paragraph_format'):
                val = getattr(style.paragraph_format, attr_name)
                if val is not None:
                    return val
            style = style.base_style
            
        # 3. Döküman Varsayılanları
        # Not: attr_name docx.enum adlandırmasıyla docDefaults XML adlandırması farklıdır.
        # Basit eşleştirme yapıyoruz.
        return self.doc_defaults.get(attr_name)

    def get_effective_line_spacing(self, paragraph) -> float:
        """Geçerli satır aralığını bulur (float olarak)."""
        rule = self.get_effective_paragraph_attribute(paragraph, 'line_spacing_rule')
        val = self.get_effective_paragraph_attribute(paragraph, 'line_spacing')

        if rule == WD_LINE_SPACING.ONE_POINT_FIVE:
            return 1.5
        if rule == WD_LINE_SPACING.DOUBLE:
            return 2.0
        if rule == WD_LINE_SPACING.SINGLE:
            return 1.0
        
        # Eğer line_spacing bir float ise (multiple spacing)
        if isinstance(val, float):
            return val
            
        # Eğer Pt nesnesi ise (exact veya at least)
        if hasattr(val, 'pt'):
            # 12pt font için 1.5 aralık ≈ 18pt
            return round(val.pt / 12.0, 1)

        return 1.0


def get_font_size_pt(size) -> Optional[float]:
    """
    python-docx font size nesnesini puntoya çevirir.
    
    Args:
        size: python-docx Pt, Emu veya int değeri
    
    Returns:
        Punto cinsinden değer veya None
    """
    if size is None:
        return None
    
    # Eğer Pt nesnesi ise
    if hasattr(size, 'pt'):
        return size.pt
    
    # Eğer int (EMU) ise
    if isinstance(size, int):
        return emu_to_pt(size)
    
    return None


def get_spacing_pt(spacing) -> Optional[float]:
    """
    Satır aralığı değerini işler.
    
    Args:
        spacing: python-docx spacing değeri
    
    Returns:
        Satır aralığı değeri veya None
    """
    if spacing is None:
        return None
    
    # Twips cinsinden ise
    if hasattr(spacing, 'pt'):
        return spacing.pt
    
    if isinstance(spacing, int):
        return twips_to_pt(spacing)
    
    return spacing


# === REGEX DESENLERİ ===

def is_chapter_heading(text: str) -> bool:
    """
    Metnin bölüm başlığı olup olmadığını kontrol eder.
    
    Bölüm başlıkları:
    - BİRİNCİ BÖLÜM, İKİNCİ BÖLÜM, ...
    - GİRİŞ, SONUÇ, KAYNAKÇA, vb.
    """
    text = text.strip().upper()
    
    patterns = [
        r"^(BİRİNCİ|İKİNCİ|ÜÇÜNCÜ|DÖRDÜNCÜ|BEŞİNCİ|ALTINCI|YEDİNCİ|SEKİZİNCİ|DOKUZUNCU|ONUNCU)\s+BÖLÜM$",
        r"^GİRİŞ$",
        r"^SONUÇ(\s+VE\s+ÖNERİLER)?$",
        r"^KAYNAKÇA$",
        r"^ÖZET$",
        r"^ABSTRACT$",
        r"^ÖN\s*SÖZ$",
        r"^İÇİNDEKİLER$",
        r"^TABLOLAR\s+LİSTESİ$",
        r"^ŞEKİLLER\s+LİSTESİ$",
        r"^SİMGELER\s+[Vv][Ee]\s+KISALTMALAR\s+LİSTESİ$",
        r"^EKLER$",  # Sadece "EKLER" - "EK 1." gibi başlıklar değil
        r"^ETİK\s+KURUL\s+ONAYI$",
        r"^BİLİMSEL\s+ETİĞE\s+UYGUNLUK$",
        r"^TEZ\s+ÖZGÜNLÜK\s+SAYFASI$",
        r"^KILAVUZA\s+UYGUNLUK$",
        r"^KABUL\s+VE\s+ONAY\s+TUTANAĞI$",
    ]
    
    for pattern in patterns:
        if re.match(pattern, text, re.IGNORECASE | re.UNICODE):
            return True
    return False


def is_numbered_heading(text: str) -> Tuple[bool, Optional[int]]:
    """
    Metnin numaralı başlık olup olmadığını kontrol eder.
    
    Döndürür:
        (is_heading, level) - level: 1, 2, veya 3
    
    Örnekler:
        "1. Giriş" -> (True, 1)
        "1.1. Alt Başlık" -> (True, 2)
        "1.1.1. Alt Alt Başlık" -> (True, 3)
        "3. sınıf öğrencileri..." -> (False, None) - küçük harfle başlıyor
    """
    text = text.strip()
    
    # 1.1.1. format (3. seviye) - numara sonrası BÜYÜK harf ile başlamalı
    match = re.match(r"^\d+\.\d+\.\d+\.\s+([A-ZÇĞİÖŞÜ])", text)
    if match:
        return (True, 3)
    
    # 1.1. format (2. seviye)
    match = re.match(r"^\d+\.\d+\.\s+([A-ZÇĞİÖŞÜ])", text)
    if match:
        return (True, 2)
    
    # 1. format (1. seviye)
    match = re.match(r"^\d+\.\s+([A-ZÇĞİÖŞÜ])", text)
    if match:
        return (True, 1)
    
    return (False, None)


def is_table_caption(text: str) -> bool:
    """
    Metnin tablo başlığı olup olmadığını kontrol eder.
    
    Format: "Tablo X.Y: Başlık" veya "Tablo X. Y: Başlık"
    """
    text = text.strip()
    return bool(re.match(r"^Tablo\s+\d+\.\s*\d+\s*:", text, re.IGNORECASE | re.UNICODE))


def is_figure_caption(text: str) -> bool:
    """
    Metnin şekil alt yazısı olup olmadığını kontrol eder.
    
    Format: "Şekil X.Y: Başlık" veya "Şekil X. Y: Başlık"
    """
    text = text.strip()
    return bool(re.match(r"^Şekil\s+\d+\.\s*\d+\s*:", text, re.IGNORECASE | re.UNICODE))


def extract_table_number(text: str) -> Optional[Tuple[int, int]]:
    """
    Tablo numarasını çıkarır.
    
    Args:
        text: "Tablo 1.2: ..." formatında metin
    
    Returns:
        (bölüm_no, tablo_no) veya None
    """
    match = re.match(r"^Tablo\s+(\d+)\.(\d+)\s*:", text, re.IGNORECASE | re.UNICODE)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return None


def extract_figure_number(text: str) -> Optional[Tuple[int, int]]:
    """
    Şekil numarasını çıkarır.
    
    Args:
        text: "Şekil 1.2: ..." formatında metin
    
    Returns:
        (bölüm_no, şekil_no) veya None
    """
    match = re.match(r"^Şekil\s+(\d+)\.(\d+)\s*:", text, re.IGNORECASE | re.UNICODE)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return None


def is_block_quote(paragraph) -> bool:
    """
    Paragrafın blok alıntı olup olmadığını kontrol eder.
    
    Blok alıntı özellikleri:
    - Her iki kenardan 1.25 cm girinti
    - İtalik
    - 11 punto
    """
    pf = paragraph.paragraph_format
    
    # Sol ve sağ girinti kontrolü
    left_indent = pf.left_indent
    right_indent = pf.right_indent
    
    if left_indent is not None and right_indent is not None:
        left_cm = emu_to_cm(left_indent) if isinstance(left_indent, int) else (left_indent.cm if hasattr(left_indent, 'cm') else None)
        right_cm = emu_to_cm(right_indent) if isinstance(right_indent, int) else (right_indent.cm if hasattr(right_indent, 'cm') else None)
        
        if left_cm and right_cm and left_cm >= 1.0 and right_cm >= 1.0:
            return True
    
    return False


def is_footnote_paragraph(paragraph) -> bool:
    """
    Paragrafın dipnot olup olmadığını kontrol eder (stil adına göre).
    """
    style_name = paragraph.style.name if paragraph.style else ""
    return "footnote" in style_name.lower() or "dipnot" in style_name.lower()


def is_reference_paragraph(paragraph) -> bool:
    """
    Paragrafın kaynakça girişi olup olmadığını kontrol eder.
    """
    style_name = paragraph.style.name if paragraph.style else ""
    return "bibliography" in style_name.lower() or "kaynakça" in style_name.lower() or "reference" in style_name.lower()


def get_text_snippet(text: Optional[str], max_length: int = 80) -> str:
    """
    Metinden kısa bir parça döndürür.
    
    Args:
        text: Tam metin
        max_length: Maksimum karakter sayısı
    
    Returns:
        Kısaltılmış metin
    """
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def count_words(text: str) -> int:
    """
    Metindeki kelime sayısını döndürür.
    """
    words = text.split()
    return len(words)


def is_uppercase_text(text: str) -> bool:
    """
    Metnin büyük harf olup olmadığını kontrol eder.
    Bağlaçlar (ve, veya, ile, and, or vb.) küçük harf olabilir kuralını uygular.
    """
    if not text:
        return False
        
    conjunctions = {
        "ve", "veya", "ile", "ya", "da", "de", "ki", "mi", "mı", "mu", "mü",
        "and", "or", "with", "the", "in", "on", "at", "by"
    }
    
    words = text.split()
    if not words:
        return False
        
    for word in words:
        clean_word = "".join(c for c in word if c.isalnum())
        if not clean_word:
            continue
            
        if clean_word.lower() not in conjunctions:
            if not clean_word.isupper():
                return False
                
    return True


def is_title_case(text: str) -> bool:
    """
    Her kelimenin ilk harfinin büyük olup olmadığını kontrol eder.
    
    Not: "ve", "veya", "ile", "da", "de" gibi bağlaçlar küçük kalabilir.
    """
    exceptions = {"ve", "veya", "ya", "da", "de", "ile", "ya da", "and", "or", "the", "a", "an"}
    
    words = text.split()
    for i, word in enumerate(words):
        # Sayı veya noktalama ile başlayan kelimeleri atla
        if not word or not word[0].isalpha():
            continue
        
        # İlk kelime her zaman büyük olmalı
        if i == 0:
            if not word[0].isupper():
                return False
        else:
            # Bağlaçlar küçük kalabilir
            if word.lower() in exceptions:
                continue
            if not word[0].isupper():
                return False
    
    return True


def validate_alignment(alignment, expected: str) -> bool:
    """
    Hizalamanın beklenen değere uygun olup olmadığını kontrol eder.
    
    Args:
        alignment: python-docx alignment değeri
        expected: "left", "center", "right", "justify"
    
    Returns:
        True eğer eşleşiyorsa
    """
    if alignment is None:
        return True  # Varsayılan değer kullanılıyor
    
    alignment_map = {
        0: "left",
        1: "center", 
        2: "right",
        3: "justify"
    }
    
    # WD_ALIGN_PARAGRAPH enum değerlerini kontrol et
    if hasattr(alignment, 'value'):
        actual = alignment_map.get(alignment.value, "unknown")
    elif isinstance(alignment, int):
        actual = alignment_map.get(alignment, "unknown")
    else:
        actual = str(alignment).lower()
    
    return actual == expected.lower()
def has_visible_borders(table) -> bool:
    """
    Tablonun görünür kenarlıkları olup olmadığını kontrol eder.
    Kenarlıklar 'nil' veya 'none' ise False döndürür.
    """
    try:
        tbl_pr = table._element.xpath('./w:tblPr')[0]
        borders = tbl_pr.xpath('./w:tblBorders')
        if not borders:
            return False
            
        # Herhangi bir kenarlık 'nil' değilse ve varsa görünür kabul edilir
        for side in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
            border = borders[0].xpath(f'./w:{side}')
            if border:
                val = border[0].get(qn('w:val'))
                if val and val not in ['nil', 'none']:
                    return True
    except Exception:
        pass
    return False


def is_epigraph(paragraph) -> bool:
    """
    Paragrafın epigraf (aktarılan söz) olup olmadığını kontrol eder.
    Sağa hizalı metinleri epigraph olarak değerlendirir.
    """
    pf = paragraph.paragraph_format
    # Sağa hizalı mı? (WD_ALIGN_PARAGRAPH.RIGHT = 2)
    if pf.alignment == 2 or (hasattr(pf.alignment, 'value') and pf.alignment.value == 2):
        return True
    return False


def is_short_quote(text: str) -> bool:
    """
    Metnin kısa alıntı (40 kelimeden az) olup olmadığını kontrol eder.
    """
    words = text.strip().split()
    return 0 < len(words) < 40


def is_chapter_title_only(text: str) -> bool:
    """
    Sadece 'BİRİNCİ BÖLÜM' gibi sadece bölüm numarasını içeren başlıkları bulur.
    """
    text = text.strip().upper()
    return bool(re.match(r"^(BİRİNCİ|İKİNCİ|ÜÇÜNCÜ|DÖRDÜNCÜ|BEŞİNCİ|ALTINCI|YEDİNCİ|SEKİZİNCİ|DOKUZUNCU|ONUNCU)\s+BÖLÜM$", text))


def is_dialogue_or_transcript(text: str) -> bool:
    """
    Metnin bir görüşme transkripti veya diyalog olup olmadığını kontrol eder.
    Örnek: 'A:', 'Ö1:', 'Araştırmacı:', 'Grup Problemi:'
    """
    if not text:
        return False
    # Regex: Cümle başında 'A:', 'Ö1:', 'Grup:' gibi kalıpları ara
    # Regex: ^([A-ZÖÇŞİĞÜ][a-zöçşiğü]*\s*\d*|A|K|E|Ö)\s*:
    import re
    pattern = r'^([A-ZÖÇŞİĞÜ][a-zöçşiğü]*\s*\d*|A|K|E|Ö)\s*:'
    return bool(re.match(pattern, text.strip()))


def is_list_item(paragraph) -> bool:
    """
    Paragrafın bir liste öğesi olup olmadığını kontrol eder.
    """
    # 1. XML seviyesinde numaralandırma kontrolü
    try:
        if paragraph._p.pPr is not None and paragraph._p.pPr.numPr is not None:
            return True
    except Exception:
        pass
        
    # 2. Metin başında liste işareti kontrolü
    text = paragraph.text.strip()
    if not text:
        return False
        
    list_markers = ['•', '-', '*', '+', '>']
    if text[0] in list_markers:
        return True
        
    # Sayısal liste (1., 2. veya a), b) gibi)
    import re
    if re.match(r'^\d+[\.\)]\s', text) or re.match(r'^[a-z][\.\)]\s', text, re.I):
        return True
        
    return False


def is_source_citation(text: str) -> bool:
    """
    Metnin bir kaynak gösterimi olup olmadığını kontrol eder.
    Örnek: 'Kaynak: ...', 'Source: ...'
    """
    if not text:
        return False
    text_upper = text.strip().upper()
    return text_upper.startswith("KAYNAK:") or text_upper.startswith("SOURCE:")
