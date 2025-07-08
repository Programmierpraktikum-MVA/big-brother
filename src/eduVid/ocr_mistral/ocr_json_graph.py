from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from langdetect import detect
from dotenv import load_dotenv
import os

# Load environment variables from .env.local file
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "env.local")
load_dotenv(dotenv_path=env_path)

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
print(f"DEBUG: Loading model {mistral_model_id}...")

print("DEBUG: Loading tokenizer...")
mistral_tokenizer = AutoTokenizer.from_pretrained(mistral_model_id)
print("DEBUG: Tokenizer loaded successfully")

print("DEBUG: Loading model without quantization...")
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
        
    print("DEBUG: Model loaded successfully")
    
except Exception as e:
    print(f"❌ Fehler beim Laden des Models: {e}")
    mistral_model = None

print("DEBUG: Compiling model...")
if mistral_model is not None:
    try:
        mistral_model = torch.compile(mistral_model)
        print("DEBUG: Model compiled successfully")
    except Exception as e:
        print(f"DEBUG: Model compilation failed: {e}")
        print("DEBUG: Continuing without compilation...")

    print(f"DEBUG: Model device: {mistral_model.device}")
    print(f"DEBUG: Model dtype: {mistral_model.dtype}")
    print(f"DEBUG: Available GPU memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB" if torch.cuda.is_available() else "DEBUG: No GPU available")

    # Test the model with a simple prompt
    print("DEBUG: Testing model with simple prompt...")
    try:
        test_prompt = "<s>[INST] Hello, respond with 'Test successful' [/INST]"
        test_inputs = mistral_tokenizer(test_prompt, return_tensors="pt").to(mistral_model.device)
        with torch.inference_mode():
            test_output = mistral_model.generate(
                **test_inputs,
                max_new_tokens=50,
                do_sample=False,
                temperature=0.1,
                pad_token_id=mistral_tokenizer.eos_token_id
            )
        test_response = mistral_tokenizer.decode(test_output[0], skip_special_tokens=True)
        print(f"DEBUG: Test response: {test_response}")
        print("DEBUG: Model test completed successfully")
    except Exception as e:
        print(f"DEBUG: Model test failed: {e}")
        import traceback
        traceback.print_exc()

    print("DEBUG: Mistral initialization complete. Ready for JSON generation.")
else:
    print("❌ Model konnte nicht geladen werden. JSON-Generation nicht verfügbar.")

User_input = ""

# === Prompt-Vorlage ===
### JSON
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
{text_input}

Jetzt gib die passende JSON-Ausgabe für diesen Text zurück:
"""


def generate_json(recognized_text):
    print(f"DEBUG: generate_json called with text: {recognized_text[:200]}...")
    
    if mistral_model is None:
        return '{"error": "Mistral Model nicht geladen"}'
    
    mistral_prompt = f"<s>[INST] {json_prompt.format(text_input=recognized_text)} [/INST]"
    print(f"DEBUG: Mistral prompt length: {len(mistral_prompt)}")
    
    try:
        print("DEBUG: Starting tokenization...")
        inputs = mistral_tokenizer(mistral_prompt, return_tensors="pt", truncation=True, max_length=2048)
        
        # Move inputs to same device as model
        inputs = {k: v.to(mistral_model.device) for k, v in inputs.items()}
        print(f"DEBUG: Tokenization successful, input shape: {inputs['input_ids'].shape}")
        
        eos_token_id = mistral_tokenizer.eos_token_id
        print(f"DEBUG: EOS token ID: {eos_token_id}")

        # JSON output
        print("DEBUG: Starting model generation...")
        
        with torch.no_grad():
            output = mistral_model.generate(
                **inputs,
                max_new_tokens=1000,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                eos_token_id=eos_token_id,
                pad_token_id=eos_token_id,
                use_cache=True
            )
            
        print(f"DEBUG: Model generation completed, output shape: {output.shape}")
        json_output = mistral_tokenizer.decode(output[0], skip_special_tokens=True)
        
        # Remove the original prompt from the output
        inst_end = json_output.find("[/INST]")
        if inst_end != -1:
            json_output = json_output[inst_end + 7:].strip()
        
        print(f"DEBUG: JSON output length: {len(json_output)}")
        print(f"DEBUG: JSON output preview: {json_output[:200]}...")
        return json_output
        
    except Exception as e:
        print(f"ERROR in generate_json: {str(e)}")
        import traceback
        traceback.print_exc()
        return f'{{"error": "JSON generation failed: {str(e)}"}}'