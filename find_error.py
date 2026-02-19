
with open('d:/Projetos/advtools/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "startfile" in line.lower():
            print(f"Found on line {i+1}: {line.strip()}")
