from docx import Document
import json
import re

doc = Document("1.docx")

start = int(input("Boshlanish savol: "))
end = int(input("Tugash savol: "))


def clean(t):
    return re.sub(r"\s+", " ", t).strip()


text = "\n".join(p.text for p in doc.paragraphs)

# savollarni ajratish
question_blocks = re.split(r"\n\+{4,}\n", text)

questions = []

for block in question_blocks:

    block = block.strip()
    if "====" not in block and "=====" not in block:
        continue

    parts = re.split(r"\n\s*=+\s*\n", block)

    if len(parts) < 2:
        continue

    question = clean(parts[0])
    options = []
    correct_index = None

    for opt in parts[1:]:
        opt = clean(opt)

        if not opt:
            continue

        is_correct = "#" in opt
        opt = opt.replace("#", "").strip()
        opt = opt.replace("=====", "").strip()

        if is_correct:
            correct_index = len(options)

        options.append(opt)

    if correct_index is not None and len(options) >= 2:
        questions.append({
            "question": question,
            "options": options,
            "correct_index": correct_index
        })


total = len(questions)

start = max(1, start)
end = min(end, total)

selected = questions[start-1:end]

with open("quiz_questions.json", "w", encoding="utf-8") as f:
    json.dump(selected, f, ensure_ascii=False, indent=2)


print("Topilgan savollar:", total)
print("Saqlangan:", len(selected))
print("Fayl: quiz_questions.json")