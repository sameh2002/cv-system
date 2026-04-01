import os
import json

from parsers.pdf_parser import extract_text_from_pdf
from parsers.docx_parser import extract_text_from_docx  
from processing.text_cleaner import clean_text
from processing.entity_extractor import extract_entities
from processing.chunker import create_chunks


def process_cv(file_path):

    if file_path.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_path)

    elif file_path.lower().endswith(".docx"):
        text = extract_text_from_docx(file_path)

    else:
        return None
    
    text = clean_text(text)

    entities = extract_entities(text)
    chunks = create_chunks(text)

    return {
        "file": file_path,
        "entities": entities,
        "chunks": chunks
    }


def run_pipeline(input_folder, output_file):

    results = []

    for file_name in os.listdir(input_folder):

        file_path = os.path.join(input_folder, file_name)

        if file_name.lower().endswith(".pdf") or file_name.lower().endswith(".docx"):

            print(f"Processing: {file_name}")

            cv_data = process_cv(file_path)

            if cv_data:
                results.append(cv_data)

    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"\nDone! Saved to {output_file}")