# Ollama Setup - Instrukcja

Ollama to narzędzie do uruchamiania dużych modeli językowych (LLM) lokalnie na Twoim komputerze.

## Opcja A: Docker (ZALECANE) 🐳

### 1. Uruchom Ollama w Dockerze
```bash
# Uruchom wszystkie serwisy (Qdrant + Ollama)
docker-compose up -d

# Sprawdź czy działa
docker ps
# Powinny być 2 kontenery: medisage-qdrant i medisage-ollama
```

### 2. Pobierz model Mistral do kontenera
```bash
# Wejdź do kontenera Ollama
docker exec -it medisage-ollama ollama pull mistral
```

To może zająć kilka minut (model ma ~4GB). Model zostanie zapisany w `./ollama_models/` i będzie persystentny.

Inne dostępne modele:
- `llama2` - Meta's Llama 2 (7B)
- `phi` - Microsoft Phi (2.7B, szybszy, mniej pamięci)
- `mistral` - Mistral 7B (zalecany, dobry balans)
- `gemma` - Google Gemma

### 3. Zweryfikuj że działa
```bash
curl http://localhost:11434/api/tags
```

Jeśli zobaczysz listę modeli w JSON - wszystko działa!

### 4. Przydatne komendy Docker

```bash
# Zatrzymaj wszystkie serwisy
docker-compose down

# Uruchom ponownie
docker-compose up -d

# Zobacz logi Ollama
docker logs medisage-ollama

# Wejdź do kontenera i uruchom model interaktywnie
docker exec -it medisage-ollama ollama run mistral

# Lista pobranych modeli
docker exec -it medisage-ollama ollama list

# Usuń model (jeśli chcesz zaoszczędzić miejsce)
docker exec -it medisage-ollama ollama rm mistral
```

---

## Opcja B: Natywna instalacja (alternatywa)

Jeśli wolisz zainstalować Ollama natywnie zamiast Dockera:

### macOS / Linux
```bash
# Pobierz z https://ollama.ai
# Lub na macOS:
brew install ollama
```

### Windows
Pobierz instalator z: https://ollama.ai/download

### Uruchomienie
```bash
# Pobierz model
ollama pull mistral

# Uruchom (automatycznie jako serwis)
ollama run mistral

# Sprawdź status
curl http://localhost:11434/api/tags
```

## Użycie w MediSage

Po uruchomieniu Ollama:
1. Uruchom aplikację: `streamlit run app.py`
2. W sidebar powinien pojawić się status: "✅ Ollama: działa"
3. Zadaj pytanie - odpowiedź będzie wygenerowana przez lokalny model

## Zmiana modelu

W pliku `app.py` zmień linię:
```python
OLLAMA_MODEL = "mistral"  # Zmień na "llama2", "phi", etc.
```

## Troubleshooting

### Ollama nie uruchamia się
```bash
# Uruchom ręcznie:
ollama serve
```

### Model generuje wolno
- Użyj mniejszego modelu (phi zamiast mistral)
- Upewnij się że masz wystarczająco RAM (minimum 8GB)

### Błąd "model not found"
```bash
# Pobierz model ponownie:
ollama pull mistral
```

## Przydatne komendy

```bash
# Lista pobranych modeli
ollama list

# Usuń model
ollama rm mistral

# Sprawdź logi
ollama logs
```
