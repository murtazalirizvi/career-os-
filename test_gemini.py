import os, sys
sys.path.insert(0, "Backend")

# Load .env
with open("Backend/.env") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

from app.analysis.gemini_client import is_available, generate

print(f"API key present: {is_available()}")
print(f"Key starts with: {os.getenv('GEMINI_API_KEY', '')[:10]}...")

result = generate("Say hello in one sentence.", temperature=0.3, max_tokens=50)
print(f"Response: '{result}'")
