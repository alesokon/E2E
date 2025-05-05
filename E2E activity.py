import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import PyPDF2
import docx
import time
import os
import pyperclip
# import openai  # Prozatím nevyužíváme

# API_KEY = ""
# openai.api_key = API_KEY

# Slovník ESRS témat
ESRS_TOPICS = {
    "ESRS E1 - Změna klimatu": {
        "Dílčí témata": ["Přizpůsobování se změně klimatu", "Zmírňování změny klimatu", "Energie"]
    },
    "ESRS E2 - Znečištění": {
        "Dílčí témata": ["Znečištění ovzduší", "Znečištění vod", "Znečištění půdy", "Znečištění živých organismů a potravinových zdrojů", "Látky vzbuzující obavy", "Látky vzbuzující mimořádné obavy", "Mikroplasty"]
    },
    "ESRS E3 - Voda a mořské zdroje": {
        "Dílčí témata": ["Voda (Spotřeba vody, Odběr vody, Vypouštění vody, Vypouštění vody do oceánů atd.)", "Mořské zdroje (Těžba a využití mořských zdrojů atd.)"]
    },
    "ESRS E4 - Biologická rozmanitost a ekosystémy": {
        "Dílčí témata": ["Faktory přímého dopadu na úbytek biologické rozmanitosti (Změna klimatu, Změna využívání půdy, změna ve využívání sladké a slané vody a změna ve využívání moře, Přímé využívání, Invazní nepůvodní druhy, Znečištění atd.)", "Dopady na stav druhů (Velikost populace druhů, Globální riziko vyhynutí druhů atd.)", "Dopady na rozsah a stav ekosystémů (Degradace půdy, Dezertifikace, Zakrývání půdy atd.)", "Dopady a závislosti s ohledem na ekosystémové služby"]
    },
    "ESRS E5 - Oběhové hospodářství": {
        "Dílčí témata": ["Příliv zdrojů, včetně využití zdrojů", "Odsun zdrojů souvisejících s produkty a službami", "Odpady"]
    },
    "ESRS S1 - Vlastní pracovní síla": {
        "Dílčí témata": ["Pracovní podmínky (Bezpečné zaměstnání, Pracovní doba, Přiměřené mzdy, Sociální dialog, Svoboda sdružování, existence rad zaměstnanců a právo zaměstnanců na informace, konzultace a účast, Kolektivní vyjednávání, včetně podílu pracovníků, na něž se vztahují kolektivní smlouvy, Rovnováha mezi pracovním a soukromým životem, Zdraví a bezpečnost atd.)", "Rovné zacházení a příležitosti pro všechny (Rovnost žen a mužů a stejná odměna za rovnocennou práci, Odborná příprava a rozvoj dovedností, Zaměstnávání a začleňování osob se zdravotním postižením, Opatření proti násilí a obtěžování na pracovišti, Rozmanitost atd.)", "Další práva související s prací (Dětská práce, Nucená práce, Přiměřené bydlení, Soukromí atd.)"]
    },
    "ESRS S2 - Pracovníci v hodnotovém řetězci": {
        "Dílčí témata": ["Pracovní podmínky (Bezpečné zaměstnání, Pracovní doba, Přiměřené mzdy, Sociální dialog, Svoboda sdružování, včetně existence rad zaměstnanců, Kolektivní vyjednávání, Rovnováha mezi pracovním a soukromým životem, Zdraví a bezpečnost atd.)", "Rovné zacházení a příležitosti pro všechny (Rovnost žen a mužů a stejná odměna za rovnocennou práci, Odborná příprava a rozvoj dovedností, Zaměstnávání a začleňování osob se zdravotním postižením, Opatření proti násilí a obtěžování na pracovišti, Rozmanitost atd.)", "Další práva související s prací (Dětská práce, Nucená práce, Přiměřené bydlení, Voda a sanitační zařízení, Soukromí atd.)"]
    },
    "ESRS S3 - Dotčené komunity": {
        "Dílčí témata": ["Hospodářská, sociální a kulturní práva komunit (Přiměřené bydlení, Přiměřená výživa, Voda a sanitační zařízení, Dopady související s půdou, Dopady související s bezpečností atd.)", "Občanská a politická práva komunit (Svoboda projevu, Svoboda shromažďování, Dopady na obránce lidských práv atd.)", "Práva původních obyvatel (Svobodný, předběžný a informovaný souhlas, Sebeurčení, Kulturní práva atd.)"]
    },
    "ESRS S4 - Spotřebitelé a koncoví uživatelé": {
        "Dílčí témata": ["Dopady související s informacemi pro spotřebitele a/nebo koncové uživatele (Soukromí, Svoboda projevu, Přístup ke kvalitním informacím atd.)", "Osobní bezpečnost spotřebitelů a/nebo koncových uživatelů (Zdraví a bezpečnost, Bezpečnost osoby, Ochrana dětí atd.)", "Sociální začleňování spotřebitelů a/nebo koncových uživatelů (Zákaz diskriminace, Přístup k produktům a službám, Odpovědné marketingové praktiky atd.)"]
    },
    "ESRS G1 - Chování podniků": {
        "Dílčí témata": ["Podniková kultura", "Ochrana oznamovatelů", "Dobré životní podmínky zvířat", "Politická angažovanost a lobbistické činnosti", "Řízení vztahů s dodavateli včetně platebních postupů", "Korupce a úplatkářství (Prevence a odhalovíní včetně školení, Incidenty atd.)"]
    }
}

def extract_text_from_pdf(pdf_path):
    """Extrakce textu z PDF pomocí PyPDF2."""
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

def extract_text_from_docx(docx_path):
    """Extrakce textu z DOCX pomocí python-docx."""
    doc_file = docx.Document(docx_path)
    paragraphs = [p.text for p in doc_file.paragraphs]
    return "\n".join(paragraphs)

def extract_text_from_file(file_path):
    """Načítá text z různých typů souborů (pdf, docx, txt)."""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return ""

def build_instructions(esrs_topics):
    """
    Sestaví řetězec s instrukcemi (bez samotného textu k analýze).
    Důrazně upozorní, že text k analýze může pokračovat v dalších částech.
    """
    # 1) Vytvoříme seznam ESRS témat:
    structured_topics = ""
    for category, details in esrs_topics.items():
        structured_topics += f"\n{category}:"
        for subtopic in details["Dílčí témata"]:
            structured_topics += f"\n  - {subtopic}"

    # 2) Sestavíme finální instrukce
    instructions = f"""\
Analyzuj následující text, který má obsahovat konkrétní informace o podnikových aktivitách a přiřaď informace k odpovídajícím kategoriím Evropského standardu pro vykazování udržitelnosti (ESRS) pro tento podnik.
Nejprve rozhodni, zda se jedná o relevantní podnikový text pro požadovanou analýzu a pokud ne, tak to uveď místo očekávaného výstupu.

***DŮLEŽITÉ:***
Tento text k analýze může být dodán ve více částech.
Prosím, NEZAČÍNEJ s analýzou, dokud nedostaneš poslední část promptu.
Každá část bude končit informací, zda se jedná o poslední část, nebo zda bude text ještě pokračovat.

**ESRS kategorie a témata k identifikaci:**
{structured_topics}

**Očekávaný výstup:**
- Výstup strukturuj jako tabulku témat včetně kategorií a podkategorií, příslušných informací z textu a hodnocení splnění ("ano"/"ne").
- Ke každému tématu vypiš všechny relevantní informace z textu, nebo napiš "Téma není zastoupeno", pokud pro dané téma není v textu informace.
- V samostatně uvedeném hodnocení splnění rozhodni, zda lze informaci považovat za konkrétní vykázání příslušné aktivity ve smyslu ESRS!
- V tabulce musí být uvedeny všechny katgorie a podkategorie témat. 
- Pod tabulku uveď ESG skóre (0-100), které bude věrně zachycovat rozsah a kvalitu plnění všech ESG aktivit a pak dílčí skóre (0-100) samostatně pro E, S a G.
- Pokud jsou v textu uvedeny potřebné finanční ukazatele, tak extrahuj, vypočti a uveď pod sebou Tržby, EBITDA, Čistý zisk, Celková aktiva, ROA (jako Čistý zisk/Celková aktiva) a ROE (jako Čistý zisk/Vlastní kapitál).

Níže už bude následovat samotný text k analýze (případně rozdělen do více částí):
"""
    return instructions.strip()

def prepare_analysis_chunks(analysis_text, max_size=50000):
    """
    Rozseká samotný "text k analýze" na chunky,
    tak aby každá část nepřesáhla ~max_size znaků.
    Rozdělení se snažíme dělat po tečkách.
    """
    sentences = analysis_text.split('.')
    chunks = []
    current_sentences = []
    current_length = 0

    for raw_sentence in sentences:
        sentence = raw_sentence.strip()
        if not sentence:
            continue

        # Přidáme tečku zpátky (plus mezera)
        sentence_with_dot = sentence + '. '
        length_with_dot = len(sentence_with_dot)

        # Pokud by přidání této věty překročilo limit, uložíme dosavadní chunk
        if current_length + length_with_dot > max_size and current_sentences:
            chunk_text = ' '.join(current_sentences).strip()
            chunks.append(chunk_text)
            current_sentences = [sentence_with_dot]
            current_length = length_with_dot
        else:
            current_sentences.append(sentence_with_dot)
            current_length += length_with_dot

    # Zpracování posledního chunku
    if current_sentences:
        chunk_text = ' '.join(current_sentences).strip()
        chunks.append(chunk_text)

    return chunks

def combine_instructions_and_chunks(instructions, analysis_chunks):
    """
    Spojí instructions s první částí analyzovaného textu.
    Každý chunk nakonec doplní o informaci, zda bude text pokračovat, nebo ne.
    """
    prompt_chunks = []
    if not analysis_chunks:
        # Kdyby náhodou text k analýze byl prázdný
        # Vrátíme pouze instructions jako 1 chunk (a je to poslední).
        prompt_chunks.append(
            instructions
            + "\n\n[Toto je poslední (a zároveň jediná) část promptu, můžeš začít zpracovávat.]\n"
        )
        return prompt_chunks

    total_chunks = len(analysis_chunks)

    # 1) První chunk = instructions + první část textu
    first_chunk_text = instructions + "\n\n" + analysis_chunks[0]
    # Pokud máme víc chunků, doplníme poznámku o pokračování,
    # jinak poznámku, že je to poslední část.
    if total_chunks > 1:
        first_chunk_text += "\n\n[Pozor, prompt bude pokračovat v další části. Nezahajuj zpracování.]\n"
    else:
        first_chunk_text += "\n\n[Toto je poslední část promptu, nyní můžeš začít zpracovávat.]\n"

    prompt_chunks.append(first_chunk_text)

    # 2) Všechny zbývající chunky
    for i in range(1, total_chunks):
        chunk_text = analysis_chunks[i]
        if i < total_chunks - 1:
            # je to prostřední chunk
            chunk_text += "\n\n[Pozor, prompt bude pokračovat v další části. Nezahajuj zpracování.]\n"
        else:
            # je to poslední chunk
            chunk_text += "\n\n[Toto je poslední část promptu, nyní můžeš začít zpracovávat.]\n"
        prompt_chunks.append(chunk_text)

    return prompt_chunks

# --- Globální proměnné pro práci s chunky ---
prompt_chunks = []
current_chunk_index = 0

def load_file():
    """Načte soubor a zobrazí jeho obsah v textovém poli."""
    file_path = filedialog.askopenfilename(
        filetypes=[("PDF files", "*.pdf"),
                   ("Text files", "*.txt"),
                   ("Word files", "*.docx")]
    )
    if file_path:
        text = extract_text_from_file(file_path)
        text_area.delete("1.0", tk.END)
        text_area.insert(tk.END, text)

def display_chunk(index):
    """
    Zobrazí chunk s daným indexem v answer_area
    a upraví text tlačítka pro kopírování, aby odpovídal pořadí.
    """
    global prompt_chunks, current_chunk_index

    if 0 <= index < len(prompt_chunks):
        answer_area.delete("1.0", tk.END)
        answer_area.insert(tk.END, prompt_chunks[index])

        # Nastavení popisku tlačítka: "Zkopírovat {index+1}. část"
        copy_button.config(text=f"Zkopírovat {index + 1}. část")
    else:
        pass  # Pokud index není v platném rozsahu, nic neděláme

def copy_current_chunk():
    """
    Zkopíruje aktuálně zobrazený chunk do schránky
    a pokusí se zobrazit následující chunk, pokud existuje.
    """
    global prompt_chunks, current_chunk_index

    if not prompt_chunks:
        messagebox.showwarning("Upozornění", "Žádná data k zkopírování.")
        return

    # Zkopíruj aktuální chunk
    current_text = prompt_chunks[current_chunk_index]
    pyperclip.copy(current_text)

    # Posuň se na další chunk
    if current_chunk_index < len(prompt_chunks) - 1:
        current_chunk_index += 1
        display_chunk(current_chunk_index)
    else:
        # Jsme u posledního chunku
        messagebox.showinfo("Hotovo", "Zkopírovali jste poslední část promptu.")

def analyze():
    """
    Spustí analýzu zadaného textu podle ESRS témat (zatím bez volání OpenAI).
    Rozdělí výsledný prompt na více částí, pokud je příliš dlouhý.
    """
    global prompt_chunks, current_chunk_index

    text = text_area.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Upozornění", "Textové pole je prázdné.")
        return

    # 1) Postavíme zvlášť "instrukce"
    instructions = build_instructions(ESRS_TOPICS)

    # 2) Samostatně máme "analysis_text" (samotný text k analýze)
    analysis_text = text

    # 3) Rozsekáme "analysis_text" na chunkové části
    analysis_chunks = prepare_analysis_chunks(analysis_text, max_size=50000)

    # 4) První chunk = instructions + 1. část
    #    Další chunky = pokračování textu
    prompt_chunks = combine_instructions_and_chunks(instructions, analysis_chunks)

    # 5) Začneme od chunku s indexem 0
    current_chunk_index = 0
    display_chunk(current_chunk_index)

    # Pokud bychom chtěli reálně volat OpenAI, stačí odkomentovat (a upravit) níže:
    # full_prompt = "\n\n".join(prompt_chunks)  # Např. poslat vše najednou
    # try:
    #     response = openai.ChatCompletion.create(
    #         model="gpt-3.5-turbo",
    #         messages=[{"role": "user", "content": full_prompt}]
    #     )
    #     answer = response.choices[0].message.content.strip()
    #     # Zobrazení celé odpovědi atd.
    # except Exception as e:
    #     messagebox.showerror("Chyba při volání OpenAI", str(e))
    #     return

# Vytvoření hlavního okna
root = tk.Tk()
root.title("Analýza ekonomických a ESG informací")
root.geometry("700x600")

# Textové pole pro zobrazení načteného obsahu
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=15)
text_area.pack(pady=10)

# Tlačítko pro načtení souboru
load_button = tk.Button(root, text="Načíst soubor", command=load_file)
load_button.pack()

# Tlačítko pro analýzu textu
analyze_button = tk.Button(root, text="Připravit pro analýzu Chatem", command=analyze)
analyze_button.pack(pady=10)

# Tlačítko pro zkopírování aktuální části
copy_button = tk.Button(root, text="Zkopírovat část", command=copy_current_chunk)
copy_button.pack(pady=10)

# Textové pole pro zobrazení chunku / promptu
answer_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=10)
answer_area.pack(pady=10)

# Spuštění hlavní smyčky Tkinter
root.mainloop()
