import os

IGNORE_DIRS = {"__init__.py", "tests", "__pycache__", ".git", "venv", ".venv", "env", ".idea", ".mypy_cache", ".vscode"}
IGNORE_FILES = {".env"}

def list_files(base_path="."):
    summary = []

    for root, dirs, files in os.walk(base_path):
        # Игнорируем ненужные папки
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        files = [f for f in files if f.endswith(".py") and f not in IGNORE_FILES]

        # Строим "относительный путь"
        rel_root = os.path.relpath(root, base_path)
        for f in files:
            path = os.path.join(rel_root, f) if rel_root != "." else f
            summary.append(path)

    return summary

def print_project_structure(base_path="."):
    print("📁 Структура проекта:\n")
    for path in list_files(base_path):
        print(f" - {path}")
    print("\n📄 Содержимое файлов:\n")

    for path in list_files(base_path):
        print(f"\n🔹 {path}:\n{'-'*60}")
        with open(os.path.join(base_path, path), "r", encoding="utf-8") as f:
            print(f.read())

if __name__ == "__main__":
    import sys
    with open('tree.txt', "w", encoding="utf-8") as f:
        sys.stdout = f  # перенаправляем print в файл
        print_project_structure()
