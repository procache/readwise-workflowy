#!/usr/bin/env python3
"""
Readwise Highlights to Markdown Converter
==========================================
Převádí XLSX export z Readwise do markdown formátu.

Použití:
    python readwise_to_markdown.py vstup.xlsx vystup.md
    
    Nebo jen:
    python readwise_to_markdown.py vstup.xlsx
    (vytvoří readwise_highlights.md v aktuálním adresáři)
"""

import sys
import pandas as pd
from pathlib import Path


def convert_highlights_to_markdown(input_file, output_file=None):
    """
    Převede XLSX soubor s highlights do markdown formátu.
    
    Args:
        input_file: Cesta k vstupnímu XLSX souboru
        output_file: Cesta k výstupnímu MD souboru (volitelné)
    
    Returns:
        tuple: (počet převedených highlights, cesta k výstupnímu souboru)
    """
    
    # Načtení dat bez hlaviček (první řádek obsahuje data)
    df = pd.read_excel(input_file, header=None)
    
    # Pojmenování sloupců podle struktury Readwise exportu
    df.columns = [
        'highlight_text',  # Text highlightu
        'article_title',   # Název článku/zdroje
        'author',          # Autor
        'col3',           # Nepoužito
        'col4',           # Nepoužito
        'col5',           # Nepoužito
        'tags',           # Tagy (oddělené čárkami)
        'col7',           # Nepoužito
        'id',             # ID highlightu
        'timestamp',      # Časová značka
        'col10'           # Nepoužito
    ]
    
    # Vytvoření markdown obsahu
    markdown_lines = []
    processed_count = 0
    
    for idx, row in df.iterrows():
        # Přeskočit řádky bez základních dat
        if pd.isna(row['article_title']) or pd.isna(row['highlight_text']):
            continue
        
        # Název článku jako nadpis
        article_title = str(row['article_title']).strip()
        markdown_lines.append(article_title)
        
        # Zpracování autora
        author = str(row['author']).strip() if pd.notna(row['author']) else "Unknown"
        
        # Zpracování tagů - použít první tag
        tags = str(row['tags']).strip() if pd.notna(row['tags']) else ""
        first_tag = tags.split(',')[0].strip() if tags else "article"
        
        # Formát: > #tag by autor
        markdown_lines.append(f"> #{first_tag} by {author}")
        
        # Text highlightu s odrážkou
        highlight_text = str(row['highlight_text']).strip()
        markdown_lines.append(f"- {highlight_text}")
        
        # Prázdný řádek mezi záznamy pro lepší čitelnost
        markdown_lines.append("")
        
        processed_count += 1
    
    # Určení výstupního souboru
    if output_file is None:
        output_file = "readwise_highlights.md"
    
    output_path = Path(output_file)
    
    # Uložení do souboru s UTF-8 kódováním (pro české znaky)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(markdown_lines))
    
    return processed_count, output_path


def main():
    """Hlavní funkce pro spuštění z příkazové řádky."""
    
    # Kontrola argumentů
    if len(sys.argv) < 2:
        print("Použití: python readwise_to_markdown.py <vstupní_soubor.xlsx> [výstupní_soubor.md]")
        print("\nPříklad:")
        print("  python readwise_to_markdown.py todo.xlsx")
        print("  python readwise_to_markdown.py todo.xlsx moje_highlights.md")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Kontrola existence vstupního souboru
    if not Path(input_file).exists():
        print(f"❌ Soubor '{input_file}' nebyl nalezen!")
        sys.exit(1)
    
    try:
        print(f"📖 Načítám highlights z '{input_file}'...")
        count, output_path = convert_highlights_to_markdown(input_file, output_file)
        
        print(f"✅ Úspěšně převedeno {count} highlights")
        print(f"📄 Výstup uložen do: {output_path}")
        print(f"📊 Velikost výstupního souboru: {output_path.stat().st_size:,} bytů")
        
    except Exception as e:
        print(f"❌ Chyba při zpracování: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
