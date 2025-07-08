from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
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

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True, 
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    llm_int8_enable_fp32_cpu_offload=True
)

mistral_tokenizer = AutoTokenizer.from_pretrained(mistral_model_id)
mistral_model = AutoModelForCausalLM.from_pretrained(
    mistral_model_id,
    quantization_config=bnb_config,  # Quantisierung aktivieren
    device_map="auto",
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True
)
mistral_model = torch.compile(mistral_model)

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

    
    detected_language = detect(recognized_text)

   
    if detected_language == "de":
        mistral_prompt = mistral_prompt_de.format(User_input=recognized_text)
    else:
        mistral_prompt = mistral_prompt_eng.format(User_input=recognized_text)

   
    inputs = mistral_tokenizer(mistral_prompt, return_tensors="pt").to(mistral_model.device)

    output = mistral_model.generate(
        **inputs,
        max_new_tokens=250,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
        pad_token_id=mistral_tokenizer.eos_token_id
    )

    
    text_output = mistral_tokenizer.decode(output[0], skip_special_tokens=True)
    return text_output

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