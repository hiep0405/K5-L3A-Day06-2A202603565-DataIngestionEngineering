import os
import sys

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from huggingface_hub import snapshot_download
from sentence_transformers import SentenceTransformer

model_id = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
print(f"Downloading essential files for {model_id} via {os.environ.get('HF_ENDPOINT')}...")

snapshot_download(
    repo_id=model_id,
    allow_patterns=[
        "config.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "special_tokens_map.json",
        "sentence_bert_config.json",
        "modules.json",
        "1_Pooling/*",
        "model.safetensors"
    ]
)
print("Essential files downloaded!")

print("Loading SentenceTransformer model...")
model = SentenceTransformer(model_id)
vec = model.encode(["Xin chào Việt Nam"])
print("SUCCESS! Model loaded. Embedding dimensions:", len(vec[0]))
