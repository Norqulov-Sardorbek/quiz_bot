from rdocx import Document
import json

doc = Document("/quizes/TEST_HEMIS_TAD_INNO_UZB_2025.docx")
text = "\n".join(p.text for p in doc.paragraphs)

questions = []

blocks = text.split("+++++")

for block in blocks:
    lines = [l.strip() for l in block.splitlines() if l.strip()]
    if len(lines) < 5:
        continue

    question = lines[0]
    options = []
    correct_index = None

    for line in lines[1:]:
        if line.startswith("#"):
            options.append(line[1:].strip())
            correct_index = len(options) - 1
        elif not line.startswith("=====") and not line.startswith("ANSWER"):
            options.append(line.strip())

    if correct_index is not None and len(options) == 4:
        questions.append({
            "question": question,
            "options": options,
            "correct_index": correct_index
        })

with open("quiz_questions.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)
