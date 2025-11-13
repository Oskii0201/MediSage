# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**MediSage** (Medical Sage) is a Deep Learning and AI course project that answers medical questions about medications based on official leaflets.

### Three Core Components:

1. **Deep Learning Models** (2 models):
   - **NER Model** - Named Entity Recognition to extract medication names from user questions
   - **Question Classifier** - Classifies question type (interactions, dosage, side effects, etc.)

2. **LLM-based Agent** - Powered by Draive framework (Miquido), uses DL models as tools to answer questions

3. **User Interface** - CLI (Command Line Interface) for interaction

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
│   ├── raw_leaflets/      # Raw medication leaflets (scraped)
│   ├── processed/          # Processed data for training
│   └── datasets/           # Training datasets (NER, classifier)
├── models/
│   ├── ner/               # NER model (BiLSTM-CRF / BERT-NER)
│   └── classifier/        # Question classifier (BERT-based)
├── src/
│   ├── ner/               # NER model code
│   ├── classifier/        # Classifier model code
│   ├── agent/             # Draive agent implementation
│   ├── database/          # Supabase integration
│   └── cli/               # CLI interface
├── notebooks/             # Jupyter notebooks for experiments
├── configs/               # Configuration files (config.yaml)
├── resources/             # Project documentation templates
├── tests/                 # Unit tests
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables (API keys)
```

## Development Setup

```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add API keys:
# - OPENAI_API_KEY or ANTHROPIC_API_KEY
# - SUPABASE_URL and SUPABASE_KEY
```

## Common Commands

```bash
# Run CLI application
python -m src.cli.main

# Train NER model
python -m src.ner.train --config configs/config.yaml

# Train question classifier
python -m src.classifier.train --config configs/config.yaml

# Scrape medication leaflets
python -m src.database.scraper --limit 100

# Run tests
pytest tests/

# Evaluate models
python -m src.ner.evaluate
python -m src.classifier.evaluate
```

## System Architecture

### Data Flow:

```
User Question: "Czy można pić alkohol z ibuprofenem?"
    ↓
[CLI] → receives input
    ↓
[Draive Agent] → orchestrates the flow
    ↓
├─ Tool 1: extract_medications()
│  └─ NER Model detects: ["ibuprofen"]
│
├─ Tool 2: classify_question()
│  └─ Classifier returns: "interakcje"
│
├─ Tool 3: get_leaflet_info(medications, category)
│  └─ Supabase query returns relevant leaflet sections
│
└─ Agent generates answer based on leaflet data
    ↓
[CLI] → displays response to user
```

### Key Design Decisions:

1. **Draive Framework** (Miquido) - Used for LLM agent instead of LangChain because:
   - Clean tool integration with @tool decorator
   - Multi-provider support (OpenAI, Anthropic, Ollama)
   - Context management
   - Production-ready observability

2. **Two DL Models** - Both required to demonstrate deep learning:
   - NER: BERT-based or BiLSTM-CRF for extracting medication names
   - Classifier: BERT-based for categorizing question types

3. **Supabase Database** - Stores medication leaflets with full-text search

4. **CLI Interface** - Saves development time vs web UI while still being functional

### Component Interfaces:

- **NER Model**: `extract_medications(text: str) -> List[str]`
- **Classifier**: `classify_question(text: str) -> str`
- **Database**: `get_leaflet_info(medications: List[str], category: str) -> str`
- **Agent**: Draive tools that wrap above functions

## Documentation Requirements

The project requires:
- A presentation with technical details and live demonstration
- A written report using the template in `resources/Report_Template.docx`
- Both should emphasize design rationale, not just implementation details
