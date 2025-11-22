"""
Załaduj dane o lekach do Qdrant (wektorowa baza danych)

Ten skrypt:
1. Wczytuje dane z openfda_medications.json
2. Tworzy embeddingi (wektory) używając sentence-transformers
3. Ładuje wszystko do Qdrant
4. Testuje wyszukiwanie

Jak uruchomić:
    python3 load_to_qdrant.py
"""

import json
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from typing import List, Dict

# Konfiguracja
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "medications"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Mały, szybki model (384 wymiary)


def load_medications(filename: str = 'data/processed/openfda_medications.json') -> List[Dict]:
    """Wczytaj dane leków z JSON."""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_fragments(medications: List[Dict]) -> List[Dict]:
    """
    Stwórz fragmenty z leków.

    Każda sekcja każdego leku = osobny fragment.
    To pozwala na precyzyjne wyszukiwanie.

    Returns:
        Lista fragmentów: {drug_name, section, text, metadata}
    """
    fragments = []

    for med in medications:
        drug_name = med['drug_name']
        sections = med['sections']

        for section_name, section_text in sections.items():
            if section_text.strip():
                fragment = {
                    'drug_name': drug_name,
                    'section': section_name,
                    'text': section_text,
                    'metadata': {
                        'source': med.get('source', 'unknown'),
                        'openfda_id': med.get('openfda_id', 'unknown')
                    }
                }
                fragments.append(fragment)

    return fragments


def initialize_qdrant(client: QdrantClient, vector_size: int):
    """
    Inicjalizuj Qdrant - stwórz kolekcję jeśli nie istnieje.

    Args:
        client: QdrantClient
        vector_size: Rozmiar wektorów (zależy od modelu embeddingów)
    """
    print(f"🔧 Inicjalizacja kolekcji '{COLLECTION_NAME}'...")

    # Sprawdź czy kolekcja istnieje
    collections = client.get_collections().collections
    collection_names = [col.name for col in collections]

    if COLLECTION_NAME in collection_names:
        print(f"  ⚠️  Kolekcja '{COLLECTION_NAME}' już istnieje - usuwam...")
        client.delete_collection(COLLECTION_NAME)

    # Stwórz nową kolekcję
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

    print(f"  ✅ Kolekcja utworzona!")
    print(f"     - Nazwa: {COLLECTION_NAME}")
    print(f"     - Rozmiar wektorów: {vector_size}")
    print(f"     - Metryka: Cosine similarity")


def main():
    """Główna funkcja."""
    print("=" * 80)
    print("📦 ŁADOWANIE DANYCH DO QDRANT")
    print("=" * 80)

    # 1. Wczytaj dane
    print("\n1️⃣  Wczytuję dane z JSON...")
    medications = load_medications()
    print(f"   ✅ Wczytano {len(medications)} leków")

    # 2. Stwórz fragmenty
    print("\n2️⃣  Tworzę fragmenty...")
    fragments = create_fragments(medications)
    print(f"   ✅ Utworzono {len(fragments)} fragmentów")

    # Pokaż przykład
    print("\n   📄 Przykładowy fragment:")
    example = fragments[0]
    print(f"      Lek: {example['drug_name']}")
    print(f"      Sekcja: {example['section']}")
    print(f"      Tekst (pierwsze 100 znaków): {example['text'][:100]}...")

    # 3. Załaduj model embeddingów
    print(f"\n3️⃣  Ładuję model embeddingów: {EMBEDDING_MODEL}")
    print(f"   (To może zająć chwilę przy pierwszym uruchomieniu...)")
    model = SentenceTransformer(EMBEDDING_MODEL)
    vector_size = model.get_sentence_embedding_dimension()
    print(f"   ✅ Model załadowany!")
    print(f"   ✅ Rozmiar wektorów: {vector_size}")

    # 4. Stwórz embeddingi
    print("\n4️⃣  Tworzę embeddingi dla wszystkich fragmentów...")
    print(f"   (Przetwarzam {len(fragments)} fragmentów...)")

    texts = [f"{frag['drug_name']} - {frag['section']}: {frag['text']}" for frag in fragments]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    print(f"   ✅ Embeddingi utworzone!")
    print(f"   ✅ Shape: {embeddings.shape}")

    # 5. Połącz się z Qdrant
    print(f"\n5️⃣  Łączę się z Qdrant ({QDRANT_HOST}:{QDRANT_PORT})...")
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    print(f"   ✅ Połączono!")

    # 6. Inicjalizuj kolekcję
    initialize_qdrant(client, vector_size)

    # 7. Ładuj dane do Qdrant
    print(f"\n6️⃣  Ładuję dane do Qdrant...")

    points = []
    for idx, (fragment, embedding) in enumerate(zip(fragments, embeddings)):
        point = PointStruct(
            id=idx,
            vector=embedding.tolist(),
            payload={
                'drug_name': fragment['drug_name'],
                'section': fragment['section'],
                'text': fragment['text'],
                'source': fragment['metadata']['source'],
                'openfda_id': fragment['metadata']['openfda_id'],
            }
        )
        points.append(point)

    # Upload w batch'ach
    client.upsert(collection_name=COLLECTION_NAME, points=points)

    print(f"   ✅ Załadowano {len(points)} punktów do Qdrant!")

    # 8. Statystyki
    print("\n" + "=" * 80)
    print("📊 PODSUMOWANIE")
    print("=" * 80)

    collection_info = client.get_collection(COLLECTION_NAME)
    print(f"✅ Kolekcja: {COLLECTION_NAME}")
    print(f"✅ Liczba wektorów: {collection_info.points_count}")
    print(f"✅ Rozmiar wektorów: {collection_info.config.params.vectors.size}")
    print(f"✅ Dashboard: http://localhost:6333/dashboard")

    # 9. Test wyszukiwania
    print("\n" + "=" * 80)
    print("🔍 TEST WYSZUKIWANIA")
    print("=" * 80)

    test_query = "Can I drink alcohol with this medication?"
    print(f"\nPytanie: \"{test_query}\"")

    # Stwórz embedding dla pytania
    query_embedding = model.encode(test_query).tolist()

    # Wyszukaj w Qdrant
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=3
    ).points

    print(f"\nTop 3 wyniki:")
    print("-" * 80)
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Lek: {result.payload['drug_name']}")
        print(f"   Sekcja: {result.payload['section']}")
        print(f"   Score: {result.score:.4f}")
        print(f"   Tekst (pierwsze 150 znaków):")
        print(f"   {result.payload['text'][:150]}...")

    print("\n" + "=" * 80)
    print("🎉 GOTOWE!")
    print("=" * 80)
    print("\nQdrant działa! Możesz teraz:")
    print("  1. Otworzyć dashboard: http://localhost:6333/dashboard")
    print("  2. Użyć Qdrant w swoich notebookach/skryptach")
    print("  3. Budować aplikację Q&A!")
    print()


if __name__ == '__main__':
    main()
