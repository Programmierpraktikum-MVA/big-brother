"""
Shared Mistral Model Manager - Singleton Pattern
Lädt das Mistral-Modell nur einmal und teilt es zwischen allen Projekten
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from dotenv import load_dotenv
import os
from threading import Lock
import time

class MistralModelManager:
    """
    Singleton class für das Mistral-Modell
    Lädt das Modell nur einmal, auch bei mehreren Importen
    """
    _instance = None
    _lock = Lock()
    _model = None
    _tokenizer = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MistralModelManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Nur einmal initialisieren
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self._load_model()
                    self._initialized = True
    
    def _load_model(self):
        """Lädt das Mistral-Modell einmalig"""
        print("\nMistral Model Manager - Einmalige Initialisierung")
        print("=" * 60)
        
        # Environment setup
        script_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(script_dir, "env.local")
        load_dotenv(dotenv_path=env_path)
        
        # HuggingFace Login
        try:
            from huggingface_hub import login
            hf_token = os.getenv("HUGGINGFACE_TOKEN")
            if hf_token:
                login(hf_token)
                print("HuggingFace Login erfolgreich")
            else:
                print("HUGGINGFACE_TOKEN nicht gesetzt")
        except Exception as e:
            print(f"HuggingFace Login fehlgeschlagen: {e}")
        
        model_id = "mistralai/Mistral-7B-Instruct-v0.3"
        
        try:
            print(f"Lade Tokenizer: {model_id}")
            self._tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                local_files_only=True
            )
            print("Tokenizer geladen")
            
            print(f"Lade Modell: {model_id}")
            start_time = time.time()
            
            if torch.cuda.is_available():
                print(f"GPU verfügbar: {torch.cuda.get_device_name(0)}")
                print(f"GPU Speicher: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB")
                
                # 4-Bit Quantisierung für optimale VRAM-Nutzung
                print("Konfiguriere 4-Bit Quantisierung (NF4)...")
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                )
                
                self._model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    quantization_config=bnb_config,
                    device_map="auto",
                    low_cpu_mem_usage=True,
                    torch_dtype=torch.float16,
                    local_files_only=True
                )
                print("Modell auf GPU geladen (4-Bit quantisiert)")
            else:
                print("Nutze CPU (GPU nicht verfügbar)")
                self._model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    torch_dtype=torch.float32,
                    device_map="cpu",
                    low_cpu_mem_usage=True,
                    local_files_only=True
                )
                print("Modell auf CPU geladen")
            
            load_time = time.time() - start_time
            print(f"Ladezeit: {load_time:.2f} Sekunden")
            
            # Modell-Test
            self._test_model()
            
            print("Mistral Model Manager erfolgreich initialisiert")
            print("=" * 60)
            
        except Exception as e:
            print(f"Fehler beim Laden des Mistral-Modells: {e}")
            import traceback
            traceback.print_exc()
            self._model = None
            self._tokenizer = None
    
    def _test_model(self):
        """Testet das Modell mit einem einfachen Prompt"""
        if self._model is None or self._tokenizer is None:
            return
            
        try:
            print("Teste Modell...")
            test_prompt = "<s>[INST] Antworte nur mit 'TEST_OK' [/INST]"
            inputs = self._tokenizer(test_prompt, return_tensors="pt").to(self._model.device)
            
            with torch.inference_mode():
                outputs = self._model.generate(
                    **inputs,
                    max_new_tokens=10,
                    do_sample=False,
                    temperature=0.1,
                    pad_token_id=self._tokenizer.eos_token_id
                )
            
            response = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"Test-Antwort: {response}")
            print("Modell-Test erfolgreich")
            
        except Exception as e:
            print(f"Modell-Test fehlgeschlagen: {e}")
    
    @property
    def model(self):
        """Gibt das geladene Modell zurück"""
        return self._model
    
    @property
    def tokenizer(self):
        """Gibt den geladenen Tokenizer zurück"""
        return self._tokenizer
    
    @property
    def is_available(self):
        """Prüft, ob das Modell verfügbar ist"""
        return self._model is not None and self._tokenizer is not None
    
    def get_memory_usage(self):
        """Gibt GPU-Speicherverbrauch zurück"""
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated(0) / (1024**3)
            reserved = torch.cuda.memory_reserved(0) / (1024**3)
            return {
                "allocated_gb": allocated,
                "reserved_gb": reserved,
                "device": torch.cuda.get_device_name(0)
            }
        return {"message": "GPU nicht verfügbar"}
    
    def generate_text(self, prompt, max_new_tokens=1000, temperature=0.7, top_p=0.9):
        """
        Generiert Text mit dem Mistral-Modell
        
        Args:
            prompt (str): Der Input-Prompt
            max_new_tokens (int): Maximale Anzahl neuer Tokens
            temperature (float): Sampling-Temperatur
            top_p (float): Nucleus sampling
            
        Returns:
            str: Generierter Text oder Fehlermeldung
        """
        if not self.is_available:
            return "Mistral-Modell nicht verfügbar"
        
        try:
            print(f"Generiere Text (max_tokens: {max_new_tokens})")
            
            inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)
            
            with torch.inference_mode():
                outputs = self._model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=temperature,
                    top_p=top_p,
                    pad_token_id=self._tokenizer.eos_token_id,
                    eos_token_id=self._tokenizer.eos_token_id
                )
            
            # Nur den neuen Text extrahieren (ohne den ursprünglichen Prompt)
            generated_text = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Entferne den ursprünglichen Prompt
            if prompt in generated_text:
                generated_text = generated_text.replace(prompt, "").strip()
            
            return generated_text
            
        except Exception as e:
            print(f"Fehler bei Textgenerierung: {e}")
            import traceback
            traceback.print_exc()
            return f"Generierungsfehler: {str(e)}"


# Globale Instanz (Singleton)
mistral_manager = MistralModelManager()


def get_mistral_manager():
    """
    Gibt die globale Mistral Manager Instanz zurück
    Das Modell wird nur beim ersten Aufruf geladen
    """
    return mistral_manager
