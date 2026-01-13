# -*- coding: utf-8 -*-
"""
EBYÜ Tez Formatlama Kontrolcüsü - Streamlit Arayüzü (v2)

Yenilikler:
- Ayarlar düzenlenebilir
- Rapor indirilebilir
- Daha temiz UI
"""

import streamlit as st
import tempfile
import os
import json
from datetime import datetime
import io

from config import ThesisConfig, DEFAULT_CONFIG
from checker import analyze_thesis

# AI Analyzer (opsiyonel - API key girilirse aktif)
try:
    from ai_analyzer import ThesisAIAnalyzer, GEMINI_AVAILABLE
except ImportError:
    GEMINI_AVAILABLE = False


# Sayfa yapılandırması
st.set_page_config(
    page_title="EBYÜ Tez Format Kontrolcüsü",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>
    .stApp { background-color: #f5f7fa; }
    .main-title { 
        font-size: 1.6rem; font-weight: bold; color: #1a365d; 
        text-align: center; margin-bottom: 0.5rem;
    }
    .sub-title { 
        font-size: 0.9rem; color: #4a5568; 
        text-align: center; margin-bottom: 1.5rem;
    }
    .error-box {
        background: #fff; border: 1px solid #e53e3e; border-left: 4px solid #e53e3e;
        padding: 0.8rem; margin: 0.5rem 0; border-radius: 4px;
    }
    .warning-box {
        background: #fffbeb; border: 1px solid #d97706; border-left: 4px solid #d97706;
        padding: 0.8rem; margin: 0.5rem 0; border-radius: 4px;
    }
    .success-box {
        background: #f0fdf4; border: 1px solid #22c55e; border-left: 4px solid #22c55e;
        padding: 1rem; border-radius: 4px; color: #166534;
    }
    .snippet {
        background: #f8fafc; border: 1px solid #e2e8f0; padding: 0.4rem 0.6rem;
        border-radius: 3px; font-family: monospace; font-size: 0.8rem;
        color: #334155; margin-top: 0.3rem;
    }
    .metric-card {
        background: #fff; border: 1px solid #e2e8f0; padding: 1rem;
        border-radius: 8px; text-align: center;
    }
    .metric-value { font-size: 1.8rem; font-weight: bold; color: #1e40af; }
    .metric-label { font-size: 0.8rem; color: #64748b; }
</style>
""", unsafe_allow_html=True)


def create_sidebar_config() -> ThesisConfig:
    """Sidebar'da düzenlenebilir konfigürasyon"""
    
    st.sidebar.markdown("## ⚙️ Denetim Ayarları")
    st.sidebar.caption("EBYÜ 2022 Kılavuzu")
    st.sidebar.markdown("---")
    
    config = ThesisConfig()
    
    # Kenar Boşlukları
    with st.sidebar.expander("📐 Kenar Boşlukları", expanded=False):
        config.margin_top = st.number_input("Üst (cm)", 1.0, 10.0, DEFAULT_CONFIG.margin_top, 0.5, key="m_top")
        config.margin_bottom = st.number_input("Alt (cm)", 1.0, 10.0, DEFAULT_CONFIG.margin_bottom, 0.5, key="m_bot")
        config.margin_left = st.number_input("Sol (cm)", 1.0, 10.0, DEFAULT_CONFIG.margin_left, 0.5, key="m_left")
        config.margin_right = st.number_input("Sağ (cm)", 1.0, 10.0, DEFAULT_CONFIG.margin_right, 0.5, key="m_right")
        config.margin_tolerance_cm = st.slider("Tolerans (cm)", 0.1, 0.5, DEFAULT_CONFIG.margin_tolerance_cm, 0.05)
    
    # Yazı Boyutları
    with st.sidebar.expander("📝 Yazı Boyutları", expanded=False):
        config.font_size_body = st.number_input("Metin (pt)", 10, 16, DEFAULT_CONFIG.font_size_body, key="fs_body")
        config.font_size_chapter_heading = st.number_input("Bölüm Başlığı (pt)", 12, 18, DEFAULT_CONFIG.font_size_chapter_heading, key="fs_ch")
        config.font_size_footnote = st.number_input("Dipnot (pt)", 8, 12, DEFAULT_CONFIG.font_size_footnote, key="fs_fn")
        config.font_size_table_content = st.number_input("Tablo İçeriği (pt)", 9, 14, DEFAULT_CONFIG.font_size_table_content, key="fs_tbl")
        config.font_size_tolerance_pt = st.slider("Tolerans (pt)", 0.1, 1.0, DEFAULT_CONFIG.font_size_tolerance_pt, 0.1)
    
    # Satır Aralığı
    with st.sidebar.expander("↕️ Satır Aralığı", expanded=False):
        config.line_spacing_body = st.number_input("Metin", 1.0, 2.5, DEFAULT_CONFIG.line_spacing_body, 0.1, key="ls_body")
        config.line_spacing_footnote = st.number_input("Dipnot/Tablo", 0.5, 2.0, DEFAULT_CONFIG.line_spacing_footnote, 0.1, key="ls_fn")
    
    # Özet
    with st.sidebar.expander("📋 Özet Kuralları", expanded=False):
        config.abstract_min_words = st.number_input("Minimum kelime", 100, 300, DEFAULT_CONFIG.abstract_min_words, 10)
        config.abstract_max_words = st.number_input("Maksimum kelime", 200, 500, DEFAULT_CONFIG.abstract_max_words, 10)
    
    # Varsayılana dön butonu
    if st.sidebar.button("🔄 Varsayılana Dön", use_container_width=True):
        st.rerun()
    
    # AI API Key
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🤖 AI Analizi")
    
    if GEMINI_AVAILABLE:
        api_key = st.sidebar.text_input(
            "🔑 Gemini API Anahtarı",
            type="password",
            help="Google AI Studio'dan API anahtarınızı alın: https://aistudio.google.com/apikey",
            key="gemini_api_key"
        )
        if api_key:
            st.sidebar.success("✓ API anahtarı girildi")
        else:
            st.sidebar.info("AI analizi için API anahtarı girin")
    else:
        st.sidebar.warning("google-generativeai paketi yüklü değil")
    
    # Buy Me a Coffee
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <a href="https://buymeacoffee.com/bbc_h" target="_blank">
        <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" 
             alt="Buy Me A Coffee" height="40" style="border-radius: 8px;">
    </a>
    <p style="font-size: 0.8rem; color: #666; margin-top: 5px;">
        Geliştirici: <strong>@bbc_h</strong>
    </p>
    """, unsafe_allow_html=True)
    
    return config


def generate_report_text(results: dict, filename: str) -> str:
    """İndirilebilir rapor oluştur"""
    
    lines = []
    lines.append("=" * 60)
    lines.append("EBYÜ TEZ FORMAT KONTROL RAPORU")
    lines.append("Erzincan Binali Yıldırım Üniversitesi")
    lines.append("=" * 60)
    lines.append(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    lines.append(f"Dosya: {filename}")
    lines.append("")
    lines.append("-" * 60)
    lines.append("ÖZET")
    lines.append("-" * 60)
    lines.append(f"Uyumluluk Skoru: %{results['compliance_score']}")
    lines.append(f"Toplam Hata: {results['total_errors']}")
    lines.append(f"Bulunan Bölümler: {results['sections_found']}/{results['sections_required']}")
    
    if results.get('abstract_word_count'):
        lines.append(f"Özet Kelime Sayısı: {results['abstract_word_count']}")
    
    # Eksik bölümler
    missing = results.get('missing_sections', [])
    if missing:
        lines.append("")
        lines.append("-" * 60)
        lines.append("EKSİK BÖLÜMLER")
        lines.append("-" * 60)
        for section in missing:
            lines.append(f"  ❌ {section}")
    
    # Hatalar
    grouped = results.get('grouped_errors', {})
    if grouped:
        lines.append("")
        lines.append("-" * 60)
        lines.append("HATALAR")
        lines.append("-" * 60)
        
        for category, segments in grouped.items():
            lines.append(f"\n📌 {category} ({len(segments)} sorun)")
            lines.append("-" * 40)
            for seg in segments:
                lines.append(f"  📍 {seg['location']}")
                for issue in seg['issues']:
                    lines.append(f"     • {issue}")
                if seg.get('snippet'):
                    lines.append(f"     > \"{seg['snippet'][:80]}...\"")
    
    if not grouped and not missing:
        lines.append("")
        lines.append("✅ Tezinizde format hatası bulunamadı!")
    
    lines.append("")
    lines.append("=" * 60)
    lines.append("Rapor Sonu")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def display_results(results: dict, filename: str, marked_doc=None):
    """Sonuçları göster"""
    
    # Metrikler
    col1, col2, col3, col4 = st.columns(4)
    
    score = results["compliance_score"]
    score_color = "#22c55e" if score >= 85 else "#eab308" if score >= 70 else "#ef4444"
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: {score_color}">%{score}</div>
            <div class="metric-label">Uyumluluk</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #ef4444">{results['total_errors']}</div>
            <div class="metric-label">Hata</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{results['sections_found']}/{results['sections_required']}</div>
            <div class="metric-label">Bölümler</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        word_count = results.get('abstract_word_count', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{word_count}</div>
            <div class="metric-label">Özet Kelime</div>
        </div>
        """, unsafe_allow_html=True)
    
    # İndirme seçenekleri
    st.markdown("---")
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        report_text = generate_report_text(results, filename)
        st.download_button(
            label="📥 Analiz Raporunu İndir (.txt)",
            data=report_text,
            file_name=f"tez_rapor_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    if marked_doc:
        doc_io = io.BytesIO()
        marked_doc.save(doc_io)
        doc_io.seek(0)
        with col_dl2:
            st.download_button(
                label="📥 İşaretlenmiş Dosyayı İndir (.docx)",
                data=doc_io,
                file_name=f"isaretlenmis_{filename}",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
    
    st.markdown("---")
    
    # Eksik bölümler
    missing = results.get('missing_sections', [])
    if missing:
        st.markdown("### ⚠️ Eksik Bölümler")
        for section in missing:
            st.markdown(f"""<div class="warning-box">❌ <strong>{section}</strong> bölümü bulunamadı</div>""", unsafe_allow_html=True)
    
    # Özet sorunları
    abstract_issues = results.get('abstract_issues', [])
    if abstract_issues:
        st.markdown("### 📝 Özet Sorunları")
        for issue in abstract_issues:
            st.markdown(f"""<div class="error-box">{issue}</div>""", unsafe_allow_html=True)
    
    # Gruplandırılmış hatalar
    grouped = results.get('grouped_errors', {})
    
    if grouped:
        st.markdown("### 🔍 Format Hataları")
        
        for category, segments in grouped.items():
            with st.expander(f"📌 {category} ({len(segments)} sorun)"):
                for seg in segments:
                    st.markdown(f"""
                    <div class="error-box">
                        <strong>📍 {seg['location']}</strong><br>
                        {'<br>'.join(['• ' + iss for iss in seg['issues']])}
                        {f'<div class="snippet">{seg["snippet"]}</div>' if seg.get('snippet') else ''}
                    </div>
                    """, unsafe_allow_html=True)
    
    elif not missing and not abstract_issues:
        st.markdown("""<div class="success-box">✅ <strong>Tebrikler!</strong> Tezinizde format hatası bulunamadı.</div>""", unsafe_allow_html=True)


def display_ai_results(results: dict):
    """AI analiz sonuçlarını göster"""
    
    # Özet sayfa kontrolü
    st.markdown("### 📋 Özet Sayfa Kontrolü")
    if results.get('abstract_overflow'):
        st.markdown(f"""<div class="warning-box">{results['abstract_message']}</div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="success-box">{results['abstract_message']}</div>""", unsafe_allow_html=True)
    
    # İstatistikler
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Toplam Kelime", f"{results.get('total_words', 0):,}")
    with col2:
        st.metric("Toplam Karakter", f"{results.get('total_chars', 0):,}")
    with col3:
        sections = results.get('sections_found', [])
        st.metric("Bulunan Bölümler", len(sections))
    
    # AI Analizi
    st.markdown("---")
    st.markdown("### 🧠 AI Mantık ve İçerik Analizi")
    st.markdown("*Gemini AI tarafından EBYÜ 2022 Kılavuzu'na göre değerlendirildi*")
    
    ai_analysis = results.get('ai_analysis', '')
    if ai_analysis:
        st.markdown(ai_analysis)
    else:
        st.warning("AI analizi yapılamadı.")


def main():
    """Ana uygulama"""
    
    st.markdown("""<div class="main-title">📄 EBYÜ Tez Format Kontrolcüsü</div>""", unsafe_allow_html=True)
    st.markdown("""<div class="sub-title">Erzincan Binali Yıldırım Üniversitesi • 2022 Kılavuzu</div>""", unsafe_allow_html=True)
    
    # Sidebar
    config = create_sidebar_config()
    
    # Tab yapısı - her zaman görünür
    tab1, tab2 = st.tabs(["📐 Format Kontrolü", "🧠 AI İçerik Analizi"])
    
    with tab1:
        st.markdown("### Format Analizi")
        st.markdown("Tezinizin EBYÜ 2022 Kılavuzu'na göre format uyumluluğunu kontrol edin.")
        
        uploaded_file_format = st.file_uploader(
            "📤 Tez dosyası (.docx)",
            type=["docx"],
            help="Word belgesi seçin",
            key="format_uploader"
        )
        
        if uploaded_file_format:
            if st.button("🔍 Format Analizi Yap", type="primary", use_container_width=True, key="format_btn"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                    tmp.write(uploaded_file_format.getvalue())
                    tmp_path = tmp.name
                
                try:
                    with st.spinner("Format analiz ediliyor..."):
                        results, marked_doc = analyze_thesis(tmp_path, config)
                    
                    display_results(results, uploaded_file_format.name, marked_doc)
                    
                except Exception as e:
                    st.error(f"Hata: {str(e)}")
                
                finally:
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
        else:
            st.info("📤 Bir .docx tez dosyası yükleyerek format analizine başlayın.")
    
    with tab2:
        st.markdown("### AI Mantık ve İçerik Analizi")
        st.markdown("Gemini AI kullanarak tezinizin mantıksal tutarlılığını ve içerik kalitesini değerlendirin.")
        
        api_key = st.session_state.get('gemini_api_key', '')
        
        if not GEMINI_AVAILABLE:
            st.error("❌ google-generativeai paketi yüklü değil. `pip install google-generativeai` komutunu çalıştırın.")
        elif not api_key:
            st.warning("⚠️ AI analizi için sol menüden Gemini API anahtarınızı girin.")
            st.markdown("""
            **API Anahtarı Nasıl Alınır?**
            1. [Google AI Studio](https://aistudio.google.com/apikey) adresine gidin
            2. "Create API Key" butonuna tıklayın
            3. Anahtarı kopyalayın ve sol menüye yapıştırın
            """)
        else:
            uploaded_file_ai = st.file_uploader(
                "📤 Tez dosyası (.docx)",
                type=["docx"],
                help="Word belgesi seçin",
                key="ai_uploader"
            )
            
            if uploaded_file_ai:
                if st.button("🧠 AI Analizi Başlat", type="primary", use_container_width=True, key="ai_btn"):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                        tmp.write(uploaded_file_ai.getvalue())
                        tmp_path = tmp.name
                    
                    try:
                        with st.spinner("AI analiz yapılıyor... (Bu işlem 30-60 saniye sürebilir)"):
                            analyzer = ThesisAIAnalyzer(api_key)
                            analyzer.load_document(tmp_path)
                            results = analyzer.analyze_thesis_content()
                        
                        display_ai_results(results)
                        
                    except Exception as e:
                        st.error(f"AI Analiz Hatası: {str(e)}")
                    
                    finally:
                        try:
                            os.unlink(tmp_path)
                        except:
                            pass
            else:
                st.info("📤 Bir .docx tez dosyası yükleyerek AI analizine başlayın.")


if __name__ == "__main__":
    main()
