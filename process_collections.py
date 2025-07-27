import os
import fitz  # PyMuPDF
from langdetect import detect
from datetime import datetime
import json
import time

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"❌ Error reading {pdf_path}: {e}")
    return text

def summarize_text(text):
    try:
        # Clean and split into sentences
        sentences = text.replace("\n", " ").split(". ")
        clean_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        # Take first 2–3 clean sentences
        summary = ". ".join(clean_sentences[:3]).strip()

        # Add period if not present
        if summary and not summary.endswith("."):
            summary += "."

        return summary
    except Exception as e:
        print(f"⚠️ Error summarizing: {e}")
        return text.strip()[:300]

def generate_output_json(collection_path):
    pdf_dir = os.path.join(collection_path, "PDFs")
    input_json_path = os.path.join(collection_path, "challenge1b_input.json")
    output_json_path = os.path.join(collection_path, "challenge1b_output.json")  # updated name

    with open(input_json_path, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    output_data = {
        "metadata": {
            "input_documents": [doc["filename"] for doc in input_data["documents"]],
            "persona": input_data["persona"]["role"],
            "job_to_be_done": input_data["job_to_be_done"]["task"],
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": [],
        "subsection_analysis": []
    }

    for idx, doc in enumerate(input_data["documents"]):
        filename = doc["filename"]
        pdf_path = os.path.join(pdf_dir, filename)

        print(f"📄 Processing: {filename}")
        text = extract_text_from_pdf(pdf_path)

        if not text.strip():
            print(f"⚠️ Skipping empty: {filename}")
            continue

        summary = summarize_text(text)

        output_data["extracted_sections"].append({
            "document": filename,
            "section_title": summary[:80] + "..." if len(summary) > 80 else summary,
            "importance_rank": idx + 1,
            "page_number": 1  # default; can refine using fitz later
        })

        output_data["subsection_analysis"].append({
            "document": filename,
            "refined_text": summary,
            "page_number": 1
        })

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"✅ challenge1b_output.json saved to: {output_json_path}")

def main():
    start = time.time()
    for folder in os.listdir(ROOT_DIR):
        collection_path = os.path.join(ROOT_DIR, folder)
        if os.path.isdir(collection_path) and "PDFs" in os.listdir(collection_path) and "challenge1b_input.json" in os.listdir(collection_path):
            print(f"\n🔍 Processing Collection: {folder}")
            generate_output_json(collection_path)
    print(f"\n✅ Done in {round(time.time() - start, 2)} seconds")

if __name__ == "__main__":
    main()
