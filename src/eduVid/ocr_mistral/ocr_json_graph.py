from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch
from langdetect import detect
import os

# ========== Mistral ==========
print("\n=== Mistral (Mistral-7B-Instruct-v0.3) ===")
from huggingface_hub import login

# Use environment variable for the token
hf_token = os.getenv("HUGGINGFACE_TOKEN")
if hf_token:
    login(hf_token)
    print("Login erfolgreich.")
else:
    print("Warning: HUGGINGFACE_TOKEN environment variable not set. Some features may not work.")

mistral_model_id = "mistralai/Mistral-7B-Instruct-v0.3"

bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)

mistral_tokenizer = AutoTokenizer.from_pretrained(mistral_model_id)
mistral_model = AutoModelForCausalLM.from_pretrained(
    mistral_model_id,
    quantization_config=bnb_config,  # Quantisierung aktivieren
    device_map="auto",
)
mistral_model = torch.compile(mistral_model)

User_input = ""

# === Prompt-Vorlage ===
### JSON
json_prompt = f"""### Instruction:
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
3. Verwende **nur Verbindungen mit semantischem oder funktionalem Zusammenhang**, z. B. „verwendet“, „basiert auf“, „wird trainiert mit“, etc.

Wichtig:
- Gib nur gültiges JSON zurück, keine Erklärungen oder zusätzlichen Kommentare.
- Gib nicht überall automatisch ein Label an – entscheide pro Beziehung.
- **KEINE** Labels, die nur Aufzählungen, Beispiele oder Kategorien ausdrücken.
- **KEINE** Labels wie:
  - "example", "examples", "application", "applications"
  - "type", "types", "category", "subcategory"
  - "component", "instance", "variant", "form", "case"
- Verwende nur Labels, die im Text durch ein **Verhalten**, **Zweck**, **Ablauf** oder **Zusammenhang** angedeutet sind.
- Bloße Kategorisierungen oder Beispiele sollen **nicht** mit Labeln versehen werden. Ansonsten gib ein Label zur Kante.
- Alle Knoten und Verbindungen müssen sinnvoll und aus dem Text ableitbar sein.
- Schreibe Begriffe und Konzepte mit normalen Leerzeichen, nicht mit Unterstrichen (_).
- Beginne Knotenbezeichner und Labels mit Großbuchstaben.
- Vermeide Netze die nur aus zwei Knoten bestehen.

Beispieltext:
{text_output}

Jetzt gib die passende JSON-Ausgabe für diesen Text zurück:
"""


def generate_json(recognized_text):
  
    mistral_prompt = f"<s>[INST] {json_prompt.format(text_output=recognized_text)} [/INST]"

   
    inputs = mistral_tokenizer(mistral_prompt, return_tensors="pt").to(mistral_model.device)

    eos_token_id = mistral_tokenizer.eos_token_id

    # JSON output
    with torch.inference_mode():
        output = mistral_model.generate(
            **inputs,
            max_new_tokens=1000,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            eos_token_id=eos_token_id,
            pad_token_id=eos_token_id
        )

  
    json_output = mistral_tokenizer.decode(output[0], skip_special_tokens=True).replace(json_prompt, "").strip()
    print(json_output)
    return json_output