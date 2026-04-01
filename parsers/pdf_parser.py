import fitz

def extract_text_from_pdf(file_path):

    doc = fitz.open(file_path)

    text = []

    for page in doc:
        page_text = page.get_text("text")

        lines = page_text.split("\n")

        for line in lines:
            line = line.strip()

            if line:
                text.append(line)

    doc.close()  #  éviter fuite mémoire

    return "\n".join(text)