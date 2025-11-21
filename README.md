# MediSage 💊🤖

**Medical Sage** - Inteligentny asystent medyczny wykorzystujący Deep Learning i LLM do odpowiadania na pytania o leki na podstawie oficjalnych ulotek.

> ⚠️ **Bezpieczeństwo**: System odpowiada TYLKO na podstawie danych z oficjalnych ulotek leków. Nie halucynuje informacji medycznych. Jeśli informacja jest niedostępna, zaleca konsultację z lekarzem/farmaceutą.

## System Overview

```
User Question → MLP Classifier → TF-IDF Retrieval → LLM Agent → Answer
                      ↓                 ↓                ↓
                  "Category"    "Leaflet Fragments"  "Grounded Answer"
```

## Komponenty Systemu

### 1. Deep Learning Model - MLP Classifier
- **Architektura**: Multilayer Perceptron (Keras/TensorFlow)
- **Input**: TF-IDF vectors z pytań użytkownika
- **Output**: 6 kategorii (dosage, alcohol_interaction, drug_interaction, contraindications, side_effects, other)
- **Zalety**: Prosty, interpretowalny, szybki do treningu

### 2. Retrieval Module - TF-IDF Search
- **Metoda**: Cosine similarity między pytaniem a fragmentami ulotek
- **Dane**: 21 leków z oficjalnych ulotek (Acetaminophen, Ibuprofen, Aspirin, itd.)
- **Zalety**: Klasyczne, sprawdzone podejście, nie wymaga zaawansowanych embeddings

### 3. LLM Agent
- **Orchestration**: Klasyfikator → Retrieval → Generowanie odpowiedzi
- **LLM**: Dowolny lokalny model (llama.cpp, Ollama, etc.)
- **Constraint**: Odpowiedzi TYLKO na podstawie dostarczonych fragmentów ulotek

### 4. User Interface - Streamlit Web App
- Pole tekstowe do zadawania pytań
- Wyświetla: odpowiedź, kategorię pytania, źródłowe fragmenty ulotek
- Alternatywnie: CLI

## Struktura Projektu

```
.
├── data/
│   ├── processed/
│   │   ├── medications.json         # 21 leków (już pobrane!)
│   │   └── leaflet_fragments.json   # Fragmenty do wyszukiwania
│   └── questions.csv                # Dataset do treningu klasyfikatora
├── medisage/
│   ├── classifier/                  # MLP classifier
│   ├── retrieval/                   # TF-IDF retriever
│   ├── agent/                       # LLM agent logic
│   └── ui/                          # Streamlit app
├── models/                          # Wytrenowane modele
├── notebooks/                       # Jupyter notebooks
└── configs/                         # Konfiguracja
```

## Setup

```bash
# 1. Aktywuj virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Zainstaluj zależności
pip install -r requirements.txt

# 3. Skonfiguruj zmienne środowiskowe
cp .env.example .env
# Edytuj .env i dodaj endpoint lokalnego LLM (opcjonalnie)
```

## Użycie

### Uruchom Streamlit App
```bash
streamlit run medisage/ui/app.py
```

### Wytrenuj Classifier
```bash
python -m medisage.classifier.train --config configs/config.yaml
```

### Przykładowe pytania:
- "Can I drink alcohol with ibuprofen?"
- "What is the dosage for aspirin?"
- "What are the side effects of metformin?"
- "Can I take ibuprofen with aspirin?"

## Roadmap Implementacji

1. ✅ **Struktura projektu** - Czysty start, nowa architektura
2. ⏳ **Data preparation** - Przygotowanie leaflet_fragments.json i questions.csv
3. ⏳ **Classifier** - Budowa i trening MLP modelu
4. ⏳ **Retrieval** - Implementacja TF-IDF search
5. ⏳ **Agent** - Orchestration logic z LLM client
6. ⏳ **UI** - Streamlit app
7. ⏳ **Evaluation** - Metryki, testy, raport

## Wymagania Projektowe

Projekt jest oceniany na podstawie:
- 📊 Definicja problemu i analiza danych (15%)
- 💡 Innowacyjność podejścia (20%)
- 🏗️ Design systemu i uzasadnienie decyzji (15%)
- 🔬 Wyjaśnienie technik (15%)
- 📈 Ewaluacja wydajności (15%)
- 🎤 Prezentacja (20%)

## Dane - 21 Leków

System operuje na oficjalnych ulotkach następujących leków:
- **Pain relief**: Acetaminophen, Ibuprofen, Aspirin, Naproxen
- **Antibiotics**: Amoxicillin, Azithromycin, Ciprofloxacin, Doxycycline
- **Diabetes**: Metformin, Insulin (Admelog)
- **Cardiovascular**: Lisinopril, Amlodipine, Losartan, Atorvastatin, Simvastatin
- **Respiratory**: Albuterol, Cetirizine, Loratadine, Montelukast
- **Digestive**: Omeprazole, Ranitidine
- **Mental health**: Sertraline, Fluoxetine, Escitalopram

## Autorzy

Projekt zaliczeniowy z przedmiotu **Deep Learning & AI**

## Licencja

Projekt edukacyjny - Educational use only
