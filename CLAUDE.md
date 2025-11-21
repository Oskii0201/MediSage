# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**MediSage** (Medical Sage) is a Deep Learning and AI course project that answers user questions about over-the-counter (OTC) medications based on official medication leaflets. The system must NOT hallucinate medical information - all answers are grounded in provided leaflet data.

### Three Core Components:

1. **Deep Learning Model** - MLP (Multilayer Perceptron) classifier in Keras/TensorFlow
   - Classifies user questions into 6 categories: dosage, alcohol_interaction, drug_interaction, contraindications, side_effects, other
   - Uses TF-IDF features extracted from question text

2. **Retrieval Module** - TF-IDF based similarity search
   - Searches medication leaflet fragments based on question + predicted category
   - Returns top-k most relevant text snippets

3. **LLM-based Agent** - Custom implementation with local LLM support
   - Orchestrates: question → classifier → retrieval → answer generation
   - Generates answers ONLY based on retrieved leaflet fragments
   - If information is missing, says "I don't know" and recommends consulting a doctor/pharmacist

4. **User Interface** - Streamlit web app (or CLI as fallback)
   - Text input for user questions
   - Displays: answer, predicted category, source leaflet fragments

## Project Requirements

The project will be evaluated on:
- Problem definition and dataset analysis (15%)
- Novelty of approach and problem importance (20%)
- System/solution design and design rationale (15%)
- Explanation of techniques used (15%)
- Performance evaluation (15%)
- Presentation quality (20%)

## Project Structure

```
.
├── data/
│   ├── processed/
│   │   ├── medications.json         # 21 medication leaflets (already scraped!)
│   │   └── leaflet_fragments.json   # Leaflets split into searchable fragments
│   └── questions.csv                # Training dataset for classifier
├── medisage/
│   ├── classifier/
│   │   ├── data_prep.py            # Load questions.csv, TF-IDF extraction
│   │   ├── model.py                # MLP classifier (Keras/TensorFlow)
│   │   └── train.py                # Training script
│   ├── retrieval/
│   │   └── tfidf_retriever.py      # TF-IDF based similarity search
│   ├── agent/
│   │   ├── llm_client.py           # Abstraction for local LLM API
│   │   └── medisage_agent.py       # Main orchestration logic
│   └── ui/
│       └── app.py                  # Streamlit web app
├── models/
│   ├── mlp_classifier.h5           # Trained MLP model
│   └── tfidf_vectorizer.pkl        # Trained TF-IDF vectorizer
├── notebooks/
│   └── exploration.ipynb           # Data analysis & experiments
├── configs/
│   └── config.yaml                 # Configuration (LLM endpoint, etc.)
├── resources/                      # Project documentation templates
├── tests/                          # Unit tests
├── requirements.txt                # Python dependencies
└── .env                            # Environment variables (LLM API key)
```

## Development Setup

```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add:
# - LLM_API_ENDPOINT (e.g., http://localhost:8080/v1/completions)
# - LLM_API_KEY (if needed)
```

## Common Commands

```bash
# Run Streamlit app
streamlit run medisage/ui/app.py

# Train question classifier
python -m medisage.classifier.train --config configs/config.yaml

# Evaluate classifier
python -m medisage.classifier.evaluate

# Run tests
pytest tests/

# Jupyter notebook for exploration
jupyter notebook notebooks/exploration.ipynb
```

## System Architecture

### Data Flow:

```
User Question: "Can I drink alcohol with ibuprofen?"
    ↓
[Streamlit UI] → receives input
    ↓
[MediSage Agent] → orchestrates the flow
    ↓
├─ Step 1: classify_question()
│  └─ MLP Classifier predicts: "alcohol_interaction"
│
├─ Step 2: retrieve_fragments(question, category)
│  └─ TF-IDF Retriever returns top-5 relevant leaflet fragments
│
└─ Step 3: generate_answer(question, category, fragments)
   └─ LLM generates answer ONLY from provided fragments
   └─ If info missing → "I don't know, consult a doctor/pharmacist"
    ↓
[Streamlit UI] → displays answer + category + source fragments
```

### Key Design Decisions:

1. **MLP Classifier (Keras/TensorFlow)** - Simple, interpretable deep learning model:
   - Input: TF-IDF vectors (sparse features)
   - Architecture: Dense layers with ReLU, Dropout, Softmax output
   - Loss: Categorical cross-entropy
   - Easy to train and explain in the report

2. **TF-IDF Retrieval** - Classic, robust similarity search:
   - No need for complex embedding models
   - Fast cosine similarity calculation
   - Easy to replace with FAISS or other methods later (modular design)

3. **Custom LLM Agent** - Flexible, self-hosted friendly:
   - Works with any local LLM (llama.cpp, Ollama, etc.)
   - Simple HTTP API abstraction
   - No vendor lock-in (OpenAI, Anthropic, etc.)

4. **Streamlit UI** - Quick to build, looks professional:
   - Much better than CLI for demonstration
   - Shows all intermediate results (category, fragments)
   - Easy to deploy if needed

### Component Interfaces:

- **Classifier**: `classify_question(text: str) -> str`
- **Retriever**: `retrieve_fragments(question: str, category: str, top_k: int) -> List[Fragment]`
- **LLM Client**: `generate(prompt: str) -> str`
- **Agent**: `answer_question(question: str) -> dict`

### Data Schema for Leaflet Fragments:

```json
{
  "drug_name": "Ibuprofen",
  "category": "alcohol_interaction",
  "text": "Avoid alcohol while taking this medication..."
}
```

## Important Constraints

1. **No Hallucination** - LLM must ONLY answer based on provided leaflet fragments
2. **Transparency** - Always show which leaflet fragments were used
3. **Safety** - If information is missing or unclear, explicitly say "I don't know" and recommend consulting a healthcare professional
4. **Simplicity** - Code should be beginner-friendly with extensive comments and docstrings

## Documentation Requirements

The project requires:
- A presentation with technical details and live demonstration
- A written report using the template in `resources/Report_Template.docx`
- Both should emphasize:
  - Problem definition (medical misinformation, need for trusted sources)
  - System design and architecture
  - Model choice rationale (why MLP? why TF-IDF?)
  - Evaluation metrics and results
  - Limitations and future work

## Implementation Roadmap

1. **Data Preparation** - Split medications.json into leaflet_fragments.json, create questions.csv
2. **Classifier** - Build and train MLP model
3. **Retrieval** - Implement TF-IDF based search
4. **Agent** - Build orchestration logic with LLM client
5. **UI** - Create Streamlit app
6. **Evaluation** - Measure classifier accuracy, end-to-end testing
