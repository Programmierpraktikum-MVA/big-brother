from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from langdetect import detect
from dotenv import load_dotenv
import os

# Load environment variables from .env.local file
load_dotenv(dotenv_path="env.local")

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

print("🔄 Lade Mistral Model ohne Quantisierung...")

mistral_tokenizer = AutoTokenizer.from_pretrained(mistral_model_id)

# Load model without quantization
try:
    # Check if CUDA is available
    if torch.cuda.is_available():
        print(f"🎮 GPU verfügbar: {torch.cuda.get_device_name(0)}")
        mistral_model = AutoModelForCausalLM.from_pretrained(
            mistral_model_id,
            torch_dtype=torch.float16,
            device_map="auto",
            low_cpu_mem_usage=True
        )
        print("✅ Model auf GPU geladen")
    else:
        print("💻 Nutze CPU")
        mistral_model = AutoModelForCausalLM.from_pretrained(
            mistral_model_id,
            torch_dtype=torch.float32,
            device_map="cpu",
            low_cpu_mem_usage=True
        )
        print("✅ Model auf CPU geladen")
        
    # Model compilation (optional)
    try:
        mistral_model = torch.compile(mistral_model)
        print("✅ Model compilation erfolgreich")
    except Exception as e:
        print(f"⚠️  Model compilation übersprungen: {e}")
        
except Exception as e:
    print(f"❌ Fehler beim Laden des Models: {e}")
    mistral_model = None

User_input = ""

# === Prompt-Vorlage ===
### Englisch
mistral_prompt_eng = f"""### Instruction:
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
mistral_prompt_de = f"""<s>[INST]### Instruction:
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
    global mistral_tokenizer, mistral_model
    
    if mistral_model is None:
        return "Fehler: Mistral Model konnte nicht geladen werden."

    try:
        detected_language = detect(recognized_text)

        if detected_language == "de":
            mistral_prompt = mistral_prompt_de.format(User_input=recognized_text)
        else:
            mistral_prompt = mistral_prompt_eng.format(User_input=recognized_text)

        # Input preparation
        inputs = mistral_tokenizer(mistral_prompt, return_tensors="pt", truncation=True, max_length=2048)
        
        # Move inputs to same device as model
        inputs = {k: v.to(mistral_model.device) for k, v in inputs.items()}

        # Generate text
        with torch.no_grad():
            output = mistral_model.generate(
                **inputs,
                max_new_tokens=250,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=mistral_tokenizer.eos_token_id,
                use_cache=True
            )

        # Decode output
        text_output = mistral_tokenizer.decode(output[0], skip_special_tokens=True)
        return text_output
        
    except Exception as e:
        print(f"❌ Fehler bei der Text-Generation: {e}")
        return f"Fehler bei der JSON-Verarbeitung: {str(e)}"

# Chat-Instruct-Format: <s>[INST]...[/INST]
# Tokenisieren
#inputs = mistral_tokenizer(mistral_prompt, return_tensors="pt").to(mistral_model.device)

# Text generieren
#output = mistral_model.generate(
    #**inputs,
    #max_new_tokens=250,
    #temperature=0.7,
    #top_p=0.9,
    #do_sample=True,
    #pad_token_id=mistral_tokenizer.eos_token_id
#)

# Ausgabe dekodieren
#text_output = mistral_tokenizer.decode(output[0], skip_special_tokens=True)#.replace(text_prompt, "").strip()
#print(text_output)##