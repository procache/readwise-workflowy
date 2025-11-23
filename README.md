# Readwise Highlights to Markdown

Jednoduchý Python skript pro převod XLSX exportu z Readwise do čitelného markdown formátu.

## Instalace

1. Nainstaluj potřebné knihovny:
```bash
pip install -r requirements.txt
```

## Použití

### Základní použití
```bash
python readwise_to_markdown.py todo.xlsx
```
Vytvoří soubor `readwise_highlights.md` v aktuálním adresáři.

### S vlastním názvem výstupu
```bash
python readwise_to_markdown.py todo.xlsx moje_highlights.md
```

### Použití jako knihovny v jiném scriptu
```python
from readwise_to_markdown import convert_highlights_to_markdown

count, output_path = convert_highlights_to_markdown("todo.xlsx", "vystup.md")
print(f"Převedeno {count} highlights do {output_path}")
```

## Formát výstupu

Každý highlight se převede do tohoto formátu:

```markdown
Název článku
> #tag by Autor
- Text highlightu

```

**Příklad:**

```markdown
A New #1 Coding Agent
> #article by ben's bites
- The OG NotebookLM team has been building an app for the last few months. Huxe, is now public, and I've been playing with it for a while.

```

## Struktura vstupního XLSX

Skript očekává tyto sloupce (v tomto pořadí):
1. Text highlightu
2. Název článku/zdroje
3. Autor
4-6. Nepoužité sloupce
7. Tagy (oddělené čárkami)
8-11. Metadata

## Poznámky

- Skript automaticky používá **první tag** ze seznamu tagů
- České znaky jsou plně podporovány (UTF-8 kódování)
- Prázdné řádky jsou přeskočeny
- Odkazy a formátování v textu jsou zachovány
