from .shared_mistral import get_mistral_manager
from langdetect import detect
import torch

print("Mistral Slide Generator (Shared Model)")

# Lade das shared Mistral Model (Singleton)
mistral_manager = get_mistral_manager()

User_input = ""

# === Prompt-Vorlage ===
### Englisch
mistral_prompt_eng = """### Instruction:
You are helping create lecture slides from outlines.

Each slide contains 3–5 informative bullet points in english language.

Your job:
Given the "Current slide", generate a **Next slide** with 3–5 bullet points that:
- Introduce a **new related topic** or **go deeper** into a subtopic.
- Do **not repeat or rephrase** items from the current slide.
- Include at least one **concrete example**, **technique**, or **real-world application**.
- Are each **at least 8 words long** and **start with a dash (-)**.

Given the current slide with the following Content:
{User_input}

### Task:
Generate the logical next slide."""


### Deutsch
mistral_prompt_de = """<s>[INST]### Instruction:
Du hilfst bei der Erstellung von Vorlesungsfolien.
Du sollst nur die neu erstellten Stichpunkte zurückgeben. Gib **nicht** die gegebenen Inhalte wieder.

Jede Folie sollte 3-5 informative Stichpunkte in Deutsch enthalten.

Dein job:
Generiere die **nächste Folie**, basierend auf einer gegebenen Folie.
- Stelle dabei ein **neues dazu passendes Thema** oder **gehe tiefergreifend** auf ein passendes Unterthema ein.
- Gib **keine Inhalte der der gegebenen Folie** wieder und wiederhole diese auch nicht.
- Gib mindestens ein **konkretes Beispiel**, eine **Technik** oder einen **realistischen Anwendungsfall**.
- Jeder Stichpunkt soll **mindestens 7 Wörter lang** sein und mit einem **Bindestrich (-) starten**.
- Gib nur die **neue Folie** aus.

Gegeben ist eine Folie mit den folgenden Inhalten:
{User_input}

### Aufgabe:
Generiere die logische nächste Folie.[/INST]"""


def generate_next_slide(recognized_text):
    print(f"Generiere nächste Folie für: {recognized_text[:100]}...")
    print(f"Mistral Manager verfügbar: {mistral_manager.is_available}")
    
    if not mistral_manager.is_available:
        return "Fehler: Mistral Model nicht verfügbar."

    try:
        # Sprache erkennen
        detected_language = detect(recognized_text)
        print(f"Erkannte Sprache: {detected_language}")

        if detected_language == "de":
            prompt = mistral_prompt_de.format(User_input=recognized_text)
        else:
            prompt = mistral_prompt_eng.format(User_input=recognized_text)

        # Verwende den shared manager für die Generierung
        text_output = mistral_manager.generate_text(
            prompt=prompt,
            max_new_tokens=250,
            temperature=0.7,
            top_p=0.9
        )
        
        if text_output.startswith("Fehler"):
            return f"Fehler bei der Generierung: {text_output}"
        
        print(f"Folie generiert (Länge: {len(text_output)})")
        return text_output
        
    except Exception as e:
        print(f"Fehler bei der Folien-Generation: {e}")
        import traceback
        traceback.print_exc()
        return f"Fehler bei der Text-Generation: {str(e)}"


def test_slide_generation():
    """Test-Funktion für die Folien-Generierung"""
    test_input = """
    - Grundlagen der Programmiersprache Python
    - Variablen und Datentypen in Python
    - Einfache Ein- und Ausgabe-Operationen
    - Erste Programme mit print() und input()
    """
    
    print("Teste Folien-Generierung...")
    result = generate_next_slide(test_input)
    print("Generierte Folie:")
    print("-" * 40)
    print(result)
    print("-" * 40)


if __name__ == "__main__":
    test_slide_generation()