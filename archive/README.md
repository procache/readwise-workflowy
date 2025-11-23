# Readwise to Workflowy Sync

Tento nástroj exportuje vaše highlights z Readwise.io s tagem "todo" a importuje je do Workflowy.

## 🚀 Dvě verze k dispozici

Tento projekt obsahuje **dvě verze** skriptu:

### 1. `readwise_to_workflowy_wfapi.py` ⭐ **DOPORUČENO**
- Používá Python knihovnu `wfapi`
- **Spolehlivější a testovanější**
- Vyžaduje username a heslo k Workflowy
- Snadnější nastavení

### 2. `readwise_to_workflowy.py`
- Přímá komunikace s Workflowy API
- Vyžaduje Bearer token nebo Session ID
- **Může vyžadovat ladění** (API není oficiálně dokumentováno)
- Použijte, pokud nechcete zadávat heslo

**💡 Tip:** Začněte s verzí `wfapi` - je jednodušší a spolehlivější!

## Funkce

- ✅ Exportuje pouze highlights s tagem "todo" z Readwise
- ✅ Automaticky vytváří položky ve Workflowy
- ✅ Zachovává metadata (autor, zdroj, URL, poznámky)
- ✅ Podpora Readwise API v2
- ✅ Detailní error reporting
- ✅ Dvě verze pro různé use-cases

## Požadavky

- Python 3.7 nebo vyšší
- Readwise účet s API tokenem
- Workflowy účet s API přístupem

## Instalace

1. Naklonujte tento repozitář:
```bash
git clone <repository-url>
cd readwise-workflowy
```

2. Nainstalujte závislosti:
```bash
pip install -r requirements.txt
```

3. Nakonfigurujte API klíče:
```bash
cp .env.example .env
```

4. Upravte soubor `.env` a doplňte své API tokeny:
```bash
nano .env
```

## Konfigurace

### Readwise API Token

1. Přejděte na https://readwise.io/access_token
2. Zkopírujte váš API token
3. Vložte ho do `.env` souboru jako `READWISE_API_TOKEN`

### Workflowy konfigurace

Máte **dvě možnosti** podle toho, kterou verzi skriptu chcete použít:

#### Pro `readwise_to_workflowy_wfapi.py` (DOPORUČENO) ⭐

Jednoduše nastavte v `.env`:
```
WORKFLOWY_USERNAME=your_email@example.com
WORKFLOWY_PASSWORD=your_password
```

#### Pro `readwise_to_workflowy.py` (Přímé API)

Máte dvě možnosti autentizace:

**Možnost A: Bearer Token**
1. Přejděte na https://beta.workflowy.com/api-reference/
2. Získejte Bearer token podle dokumentace
3. Vložte ho do `.env` souboru jako `WORKFLOWY_BEARER_TOKEN`

**Možnost B: Session ID**
1. Přihlaste se do Workflowy ve webovém prohlížeči
2. Otevřete Developer Tools (F12)
3. Přejděte do záložky "Application" → "Cookies"
4. Najděte cookie s názvem "sessionid"
5. Zkopírujte její hodnotu
6. Vložte ji do `.env` souboru jako `WORKFLOWY_SESSION_ID`

## Použití

### Verze wfapi (Doporučeno) ⭐

```bash
python readwise_to_workflowy_wfapi.py
```

### Verze s přímým API

```bash
python readwise_to_workflowy.py
```

**Poznámka:** Pokud první verze nefunguje, zkuste druhá verzi a naopak.

Skript:
1. Ověří vaše API tokeny
2. Načte všechny highlights s tagem "todo" z Readwise
3. Vytvoří pro každý highlight novou položku ve Workflowy
4. Přidá metadata do poznámek (autor, zdroj, URL)

## Příklad výstupu

```
Initializing Readwise client...
✓ Readwise authentication successful

Initializing Workflowy client...
✓ Workflowy client initialized

Fetching highlights with tag 'todo' from Readwise...
Found 15 highlights with tag 'todo'

Creating 15 items in Workflowy...
  ✓ Created: This is an important highlight to remember...
  ✓ Created: Another useful piece of information...
  ✓ Created: Something I need to follow up on...
  ...

Successfully created 15/15 items

✓ Sync complete! 15 items created in Workflowy
```

## Struktura vytvořených položek

Každý highlight bude ve Workflowy vytvořen jako položka s následující strukturou:

**Text položky:** Samotný text highlightu

**Poznámka obsahuje:**
- Source: Název knihy/článku
- Author: Autor zdroje
- URL: Odkaz na originál (pokud existuje)
- Note: Vaše osobní poznámka k highlightu (pokud existuje)

## API Limity

- **Readwise:** 20 požadavků za minutu
- **Workflowy:** 100 nových položek za minutu

Skript tyto limity respektuje a zpracovává highlights postupně.

## Řešení problémů

### "Error: READWISE_API_TOKEN environment variable not set"

Ujistěte se, že máte vytvořený soubor `.env` a že obsahuje platný `READWISE_API_TOKEN`.

### "Error: Invalid Readwise API token"

Váš Readwise API token je neplatný. Zkontrolujte ho na https://readwise.io/access_token

### "Error: Either WORKFLOWY_BEARER_TOKEN or WORKFLOWY_SESSION_ID must be set"

Musíte nastavit alespoň jednu z metod autentizace pro Workflowy.

### Workflowy API vrací chyby

- Zkontrolujte, zda je váš Bearer token nebo Session ID stále platný
- Session ID může vypršet - zkuste ho obnovit
- Ověřte, že máte oprávnění vytvářet položky ve Workflowy

## Struktura projektu

```
readwise-workflowy/
├── readwise_to_workflowy.py  # Hlavní skript
├── requirements.txt           # Python závislosti
├── .env.example              # Vzorová konfigurace
├── .gitignore               # Git ignore soubor
└── README.md                # Tato dokumentace
```

## Bezpečnost

- **Nikdy necommitujte soubor `.env` do verzovacího systému**
- `.env` je automaticky ignorován pomocí `.gitignore`
- Své API tokeny nikomu nesdílejte
- Session ID může vypršet, Bearer token je bezpečnější

## API Dokumentace

- **Readwise API:** https://readwise.io/api_deets
- **Workflowy API:** https://beta.workflowy.com/api-reference/

## Licence

MIT

## Autor

Vytvořeno pomocí Claude Code

## Přispívání

Pull requesty jsou vítány! Pro větší změny prosím nejdříve otevřete issue.
