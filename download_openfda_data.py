"""
Download medication data from OpenFDA API

Ten skrypt pobiera oficjalne ulotki leków z OpenFDA (FDA - US Food and Drug Administration)
i zapisuje je w czystym, strukturyzowanym formacie JSON.

Jak uruchomić:
    python3 download_openfda_data.py

Co robi:
    1. Pobiera dane z OpenFDA API dla popularnych leków
    2. Ekstrahuje najważniejsze sekcje (dawkowanie, ostrzeżenia, interakcje, etc.)
    3. Zapisuje do data/processed/openfda_medications.json
"""

import requests
import json
import time
import re
from typing import Dict, List, Optional

# Lista popularnych leków do pobrania
MEDICATIONS = [
    "Ibuprofen",
    "Acetaminophen",
    "Aspirin",
    "Naproxen",
    "Metformin",
    "Lisinopril",
    "Amlodipine",
    "Atorvastatin",
    "Omeprazole",
    "Sertraline",
]

# Mapowanie pól OpenFDA na nasze kategorie
SECTION_MAPPING = {
    # OpenFDA field → nasza kategoria
    'dosage_and_administration': 'dosage',
    'warnings': 'warnings',
    'drug_interactions': 'drug_interactions',
    'contraindications': 'contraindications',
    'adverse_reactions': 'side_effects',
    'indications_and_usage': 'indications',
    'warnings_and_cautions': 'warnings',
    'precautions': 'precautions',
    'overdosage': 'overdosage',
    'information_for_patients': 'patient_info',
}


def clean_text(text: str) -> str:
    """
    Czyści i formatuje tekst z OpenFDA.

    Problemy w surowych danych:
    - Brak znaków interpunkcyjnych
    - Nadmiarowe spacje
    - Dziwne znaki

    Args:
        text: Surowy tekst

    Returns:
        Wyczyszczony tekst
    """
    if not text:
        return ""

    # Usuń nadmiarowe spacje
    text = re.sub(r'\s+', ' ', text)

    # Usuń dziwne znaki kontrolne
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

    # Dodaj kropki po typowych skrótach jeśli brakuje
    text = re.sub(r'\b(Dr|Mr|Mrs|Ms|vs|etc|approx|max|min)\b(?!\.)', r'\1.', text)

    # Popraw formatowanie list (jeśli są)
    text = re.sub(r'(\d+)\s*\)', r'\n\1)', text)  # "1)" -> "\n1)"
    text = re.sub(r'([•●○])', r'\n\1', text)  # Bullet points na nową linię

    # Trim
    text = text.strip()

    return text


def fetch_drug_from_openfda(drug_name: str) -> Optional[Dict]:
    """
    Pobierz dane leku z OpenFDA API.

    Args:
        drug_name: Nazwa leku (np. "Ibuprofen")

    Returns:
        Dict z danymi leku lub None jeśli nie znaleziono
    """
    # OpenFDA API endpoint
    base_url = "https://api.fda.gov/drug/label.json"

    # Parametry wyszukiwania
    params = {
        'search': f'openfda.generic_name:"{drug_name}" OR openfda.brand_name:"{drug_name}"',
        'limit': 1  # Pobierz tylko pierwszy wynik
    }

    try:
        print(f"  📡 Wysyłam request do OpenFDA...")
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if 'results' not in data or len(data['results']) == 0:
            print(f"  ❌ Nie znaleziono danych dla {drug_name}")
            return None

        return data['results'][0]

    except requests.exceptions.RequestException as e:
        print(f"  ❌ Błąd podczas pobierania {drug_name}: {e}")
        return None


def extract_sections(raw_data: Dict) -> Dict[str, str]:
    """
    Wyekstrahuj sekcje z surowych danych OpenFDA.

    OpenFDA zwraca sekcje jako listy stringów. Łączymy je w jeden tekst.

    Args:
        raw_data: Surowe dane z OpenFDA

    Returns:
        Dict z sekcjami {nazwa_sekcji: tekst}
    """
    sections = {}

    for openfda_field, our_category in SECTION_MAPPING.items():
        if openfda_field in raw_data:
            # OpenFDA zwraca listy stringów - złącz je
            field_data = raw_data[openfda_field]

            if isinstance(field_data, list):
                text = ' '.join(field_data)
            else:
                text = str(field_data)

            # WYCZYŚĆ TEKST!
            cleaned_text = clean_text(text)

            # Zapisz tylko jeśli nie jest puste
            if cleaned_text:
                sections[our_category] = cleaned_text

    return sections


def extract_drug_name(raw_data: Dict) -> str:
    """
    Wyekstrahuj nazwę leku z danych OpenFDA.

    Strategia:
    1. Spróbuj openfda.generic_name
    2. Spróbuj openfda.brand_name
    3. Użyj "Unknown" jako fallback
    """
    openfda = raw_data.get('openfda', {})

    # Spróbuj generic name (np. "Ibuprofen")
    if 'generic_name' in openfda and openfda['generic_name']:
        return openfda['generic_name'][0].title()

    # Spróbuj brand name (np. "Advil")
    if 'brand_name' in openfda and openfda['brand_name']:
        return openfda['brand_name'][0].title()

    return "Unknown"


def download_all_medications() -> List[Dict]:
    """
    Pobierz wszystkie leki z listy MEDICATIONS.

    Returns:
        Lista słowników z danymi leków
    """
    medications_data = []

    print("=" * 80)
    print("🏥 POBIERANIE DANYCH Z OPENFDA")
    print("=" * 80)
    print(f"\nLiczba leków do pobrania: {len(MEDICATIONS)}\n")

    for i, drug_name in enumerate(MEDICATIONS, 1):
        print(f"[{i}/{len(MEDICATIONS)}] Pobieram: {drug_name}")

        # Pobierz surowe dane
        raw_data = fetch_drug_from_openfda(drug_name)

        if raw_data is None:
            print(f"  ⏭️  Pomijam {drug_name}\n")
            continue

        # Wyekstrahuj nazwę i sekcje
        extracted_name = extract_drug_name(raw_data)
        sections = extract_sections(raw_data)

        print(f"  ✅ Nazwa: {extracted_name}")
        print(f"  ✅ Sekcji znalezionych: {len(sections)}")

        # Stwórz czysty wpis
        clean_entry = {
            'drug_name': extracted_name,
            'sections': sections,
            'source': 'OpenFDA',
            'openfda_id': raw_data.get('id', 'unknown')
        }

        medications_data.append(clean_entry)
        print(f"  ✅ Dodano do listy!\n")

        # Odczekaj chwilę żeby nie spamować API (rate limiting)
        time.sleep(0.5)

    return medications_data


def save_to_json(data: List[Dict], filename: str):
    """Zapisz dane do pliku JSON."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Zapisano do: {filename}")


def main():
    """Główna funkcja."""
    # Pobierz dane
    medications = download_all_medications()

    # Podsumowanie
    print("=" * 80)
    print("📊 PODSUMOWANIE")
    print("=" * 80)
    print(f"✅ Pobrano: {len(medications)} leków")

    if medications:
        total_sections = sum(len(med['sections']) for med in medications)
        print(f"✅ Całkowita liczba sekcji: {total_sections}")
        print(f"✅ Średnio {total_sections / len(medications):.1f} sekcji na lek")

        # Zapisz
        output_file = 'data/processed/openfda_medications.json'
        save_to_json(medications, output_file)

        # Pokaż listę pobranych leków
        print("\n📋 Lista pobranych leków:")
        print("-" * 80)
        for i, med in enumerate(medications, 1):
            num_sections = len(med['sections'])
            print(f"{i:2}. {med['drug_name']:20} ({num_sections} sekcji)")

        print("\n" + "=" * 80)
        print("🎉 GOTOWE!")
        print("=" * 80)
        print(f"\nMożesz teraz użyć pliku: {output_file}")
        print("w swoich notebookach do wyszukiwania!\n")
    else:
        print("❌ Nie udało się pobrać żadnych leków")
        print("Sprawdź połączenie internetowe i spróbuj ponownie.")


if __name__ == '__main__':
    main()
