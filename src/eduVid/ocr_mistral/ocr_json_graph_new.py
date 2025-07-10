"""
Optimized OCR JSON Graph Generation with Shared Mistral Model
Uses singleton pattern to prevent multiple model loading
"""

from shared_mistral import get_mistral_manager
import json

# Lade das shared Mistral Model (Singleton)
print("🔗 Verbinde mit shared Mistral Manager...")
mistral_manager = get_mistral_manager()

# JSON Prompt Template
json_prompt = """### Instruction:
Du bist ein JSON-Assistent.

Deine Aufgabe ist es, aus einem Text mit Stichpunkten eine JSON-Struktur für einen Wissensgraphen zu erstellen.

Formatvorgabe (bitte exakt einhalten):

{{
  "nodes": [
    {{ "id": "..." }},
    ...
    {{ "id": "..." }}
  ],
  "edges": [
    {{ "from": "...", "to": "..." [, "label": "..."] }},
    ...
    {{ "from": "...", "to": "..." [, "label": "..."] }}
  ]
}}

Vorgehen:
1. Analysiere die Begriffe oder Konzepte aus dem Text → diese werden zu "nodes".
2. Erkenne sinnvolle Beziehungen oder Aktionen zwischen diesen Begriffen → diese werden zu "edges" mit passenden "labels".
3. Verwende **nur Verbindungen mit semantischem oder funktionalem Zusammenhang**, z. B. „verwendet", „basiert auf", „wird trainiert mit", etc.

Wichtig:
- Gib nur gültiges JSON zurück, keine Erklärungen oder zusätzlichen Kommentare.
- Gib nicht überall automatisch ein Label an – entscheide pro Beziehung.
- Alle Knoten und Verbindungen müssen sinnvoll und aus dem Text ableitbar sein.
- Schreibe Begriffe und Konzepte mit normalen Leerzeichen, nicht mit Unterstrichen (_).
- Beginne Knotenbezeichner und Labels mit Großbuchstaben.
- Vermeide Netze die nur aus zwei Knoten bestehen.

Beispieltext:
{text_input}

Jetzt gib die passende JSON-Ausgabe für diesen Text zurück:
"""


def generate_json(recognized_text):
    """
    Generiert JSON aus OCR-Text mit dem shared Mistral-Modell
    """
    print(f"🎯 JSON-Generierung gestartet für Text: {recognized_text[:100]}...")
    
    # Prüfe, ob das Mistral-Modell verfügbar ist
    if not mistral_manager.is_available:
        print("❌ Mistral-Modell nicht verfügbar - verwende Fallback")
        return create_fallback_json(recognized_text)
    
    try:
        # Erstelle den vollständigen Prompt
        full_prompt = f"<s>[INST] {json_prompt.format(text_input=recognized_text)} [/INST]"
        print(f"📝 Prompt-Länge: {len(full_prompt)} Zeichen")
        
        # Zeige Speicherverbrauch vor der Generierung
        memory_info = mistral_manager.get_memory_usage()
        if 'allocated_gb' in memory_info:
            print(f"💾 GPU Speicher: {memory_info['allocated_gb']:.1f} GB verwendet")
        
        # Generiere mit dem shared Manager (schnellere Einstellungen)
        print("🚀 Starte Mistral-Generierung...")
        json_output = mistral_manager.generate_text(
            prompt=full_prompt,
            max_new_tokens=400,  # Reduziert für schnellere Generierung
            temperature=0.3,     # Deterministischer
            top_p=0.8           # Fokussiertere Ausgaben
        )
        
        # Bereinige die Ausgabe
        json_output = clean_json_output(json_output)
        
        print(f"✅ JSON generiert ({len(json_output)} Zeichen)")
        print(f"📋 Preview: {json_output[:150]}...")
        
        # Validiere das JSON
        try:
            parsed = json.loads(json_output)
            nodes_count = len(parsed.get('nodes', []))
            edges_count = len(parsed.get('edges', []))
            print(f"✅ JSON ist valide (Nodes: {nodes_count}, Edges: {edges_count})")
            return json_output
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON ist nicht valide: {e}")
            print(f"🔄 Versuche Fallback-JSON...")
            return create_fallback_json(recognized_text)
        
    except Exception as e:
        print(f"❌ Fehler bei JSON-Generierung: {str(e)}")
        import traceback
        traceback.print_exc()
        return create_fallback_json(recognized_text)


def clean_json_output(raw_output):
    """
    Bereinigt die Mistral-Ausgabe und extrahiert nur das JSON
    """
    try:
        # Entferne eventuelle Präfixe
        if "[/INST]" in raw_output:
            json_part = raw_output.split("[/INST]")[-1].strip()
        else:
            json_part = raw_output.strip()
        
        # Finde den JSON-Teil (zwischen ersten { und letzten })
        start_idx = json_part.find('{')
        end_idx = json_part.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_part = json_part[start_idx:end_idx+1]
            return json_part
        
        # Fallback: return original if no JSON structure found
        return json_part
        
    except Exception as e:
        print(f"⚠️  Fehler beim Bereinigen der JSON-Ausgabe: {e}")
        return raw_output


def create_fallback_json(text):
    """
    Erstellt ein einfaches JSON-Fallback basierend auf dem Text
    """
    print("🔄 Erstelle Fallback-JSON...")
    
    try:
        # Einfache Keyword-Extraktion
        words = text.replace(',', ' ').replace('.', ' ').replace('&', ' ').split()
        important_words = [word.strip('.,;:!?-') for word in words if len(word) > 3]
        
        # Entferne Duplikate und nehme die ersten 6
        unique_words = list(dict.fromkeys(important_words))[:6]
        
        # Erstelle Nodes
        nodes = [{"id": word.capitalize()} for word in unique_words]
        
        # Erstelle einfache Verbindungen
        edges = []
        for i in range(len(unique_words) - 1):
            edges.append({
                "from": unique_words[i].capitalize(),
                "to": unique_words[i + 1].capitalize()
            })
        
        # Falls genug Begriffe vorhanden, erstelle auch thematische Verbindungen
        if len(unique_words) >= 4:
            edges.append({
                "from": unique_words[0].capitalize(),
                "to": unique_words[-1].capitalize(),
                "label": "gehört zu"
            })
        
        fallback_json = {
            "nodes": nodes,
            "edges": edges
        }
        
        result = json.dumps(fallback_json, ensure_ascii=False, indent=2)
        print(f"✅ Fallback-JSON erstellt mit {len(nodes)} Nodes und {len(edges)} Edges")
        return result
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen des Fallback-JSON: {e}")
        return '{"nodes": [{"id": "Error"}], "edges": []}'


def get_model_status():
    """
    Gibt den Status des Mistral-Modells zurück
    """
    if mistral_manager.is_available:
        memory_info = mistral_manager.get_memory_usage()
        return {
            "status": "available",
            "memory": memory_info
        }
    else:
        return {
            "status": "not_available",
            "message": "Mistral-Modell nicht geladen"
        }


def quick_test():
    """
    Schneller Test der JSON-Generierung
    """
    test_text = "Machine Learning Algorithmus Training Dataset Evaluation"
    print("🧪 Teste JSON-Generierung...")
    result = generate_json(test_text)
    print(f"🧪 Test-Ergebnis: {result}")
    return result


if __name__ == "__main__":
    print("🚀 OCR JSON Graph Generator mit Shared Mistral")
    print(f"📊 Model Status: {get_model_status()}")
    quick_test()
