import os
import re

TARGET_FILES = [
    "handlers/generation.py",
    "handlers/vectorize.py",
]

ANSWER_CALL_RE = re.compile(r'(await\s+message\.answer\(([^)]*))\)', re.DOTALL)
IMPORT_RE = re.compile(r'^from\s+keyboards\s+import\s+([^\n]+)', re.MULTILINE)

def ensure_import(code: str, func_name: str) -> str:
    """Добавляет функцию в строку импорта, либо вставляет новый импорт"""
    match = IMPORT_RE.search(code)
    if match:
        existing = match.group(1).replace(" ", "").split(",")
        if func_name not in existing:
            new_import = match.group(0).replace(match.group(1), match.group(1) + f", {func_name}")
            return code.replace(match.group(0), new_import)
        else:
            return code  # уже импортировано
    else:
        # Вставим новый импорт сразу после всех импортов
        lines = code.splitlines()
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith("#") and not line.strip().startswith("import") and not line.strip().startswith("from"):
                # Вставим до первой не-импорт строки
                lines.insert(i, f"from keyboards import {func_name}")
                break
        return "\n".join(lines)

def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    modified = False
    new_code = code

    for match in ANSWER_CALL_RE.finditer(code):
        full_call = match.group(0)
        inner = match.group(2)

        if "reply_markup=" in inner:
            continue

        fixed_call = f"{match.group(1)}, reply_markup=get_back_keyboard())"
        new_code = new_code.replace(full_call, fixed_call)
        modified = True

    if modified:
        # Добавим импорт, если надо
        new_code = ensure_import(new_code, "get_back_keyboard")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_code)
        print(f"✅ Обновлён файл: {file_path}")
    else:
        print(f"➖ Без изменений: {file_path}")

if __name__ == "__main__":
    for path in TARGET_FILES:
        if os.path.exists(path):
            process_file(path)
        else:
            print(f"❌ Файл не найден: {path}")
