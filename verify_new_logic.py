from checker import analyze_thesis
from config import ThesisConfig

def verify_file():
    doc_path = "/Users/halil/Desktop/tez kontrol/Meşru Savunmada Sınırın Aşılması.docx"
    config = ThesisConfig()
    
    print(f"Analyzing {doc_path}...")
    report, doc = analyze_thesis(doc_path, config)
    
    print("\n--- ANALYSIS SUMMARY ---")
    print(f"Compliance Score: {report['compliance_score']}%")
    print(f"Total Errors: {report['total_errors']}")
    print(f"Sections Found: {report['sections_found']}/{report['sections_required']}")
    print(f"Abstract Word Count: {report['abstract_word_count']}")
    
    if "Sonuç" in report["grouped_errors"]:
        print("\nSonuç Issues:")
        for err in report["grouped_errors"]["Sonuç"]:
            print(f"- {err['issues']}")

    output_path = "/Users/halil/Desktop/tez kontrol/isaretlenmis_mesru_savunma.docx"
    doc.save(output_path)
    print(f"\nSaved marked document to: {output_path}")

if __name__ == "__main__":
    verify_file()
