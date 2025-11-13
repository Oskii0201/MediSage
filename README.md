# MediSage

**Medical Sage** - Inteligentny asystent medyczny wykorzystujący Deep Learning i LLM do odpowiadania na pytania o leki na podstawie oficjalnych ulotek.

## Komponenty Systemu

### 1. Model Deep Learning - NER (Named Entity Recognition)
Model do automatycznego wykrywania nazw leków w pytaniach użytkownika.
- Architektura: BiLSTM-CRF / BERT-NER
- Dataset: Oznaczone pytania medyczne z nazwami substancji czynnych

### 2. Model Deep Learning - Question Classifier
Model do klasyfikacji typu pytania (interakcje, dawkowanie, skutki uboczne, etc.)
- Architektura: BERT-based classifier
- Kategorie: interakcje, dawkowanie, skutki_uboczne, przeciwwskazania, inne

### 3. LLM Agent (Draive Framework)
Agent oparty na LLM który wykorzystuje modele DL jako narzędzia i odpowiada na pytania użytkownika.
- Framework: Draive (Miquido)
- Provider: OpenAI / Anthropic / Ollama

### 4. User Interface
CLI (Command Line Interface) do interakcji z systemem.

## Struktura Projektu

```
.
├── data/
│   ├── raw_leaflets/      # Surowe ulotki leków
│   ├── processed/          # Przetworzone dane
│   └── datasets/           # Datasety treningowe
├── models/
│   ├── ner/               # Model NER
│   └── classifier/        # Model klasyfikatora
├── src/
│   ├── ner/               # Kod modelu NER
│   ├── classifier/        # Kod klasyfikatora
│   ├── agent/             # Draive agent
│   ├── database/          # Supabase integration
│   └── cli/               # CLI interface
├── notebooks/             # Jupyter notebooks do eksperymentów
├── configs/               # Pliki konfiguracyjne
└── tests/                 # Testy

```

## Setup

```bash
# Utwórz virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Zainstaluj zależności
pip install -r requirements.txt

# Skonfiguruj zmienne środowiskowe
cp .env.example .env
# Edytuj .env i dodaj swoje klucze API
```

## Użycie

```bash
# Uruchom CLI
python -m src.cli.main

# Przykład pytania:
> Czy można pić alkohol z ibuprofenem?
```

## Rozwój Projektu

1. Zbieranie danych (ulotki leków)
2. Przygotowanie datasetów do treningu
3. Trening modelu NER
4. Trening klasyfikatora pytań
5. Integracja z Draive
6. Budowa CLI
7. Testowanie i ewaluacja

## Autorzy

Projekt zaliczeniowy z przedmiotu Deep Learning & AI

## Licencja

Projekt edukacyjny
