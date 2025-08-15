from huggingface_hub import snapshot_download

# Pfad zum lokalen Ordner
local_dir = "~/big-brother/models"

# Modell-ID
model_id = "mistralai/Mistral-7B-Instruct-v0.3"

# Download starten
snapshot_download(repo_id=model_id, cache_dir=local_dir, local_files_only=False)