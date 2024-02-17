from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer
import argparse


encoder = SentenceTransformer("all-MiniLM-L6-v2")
qdrant = QdrantClient(":memory:")

def neural_search(query):
    print(f"Running neural search with term: {query}")
    hits = qdrant.search(
        collection_name="zalando",
        query_vector=encoder.encode(query).tolist(),
        limit=3,
    )
    for hit in hits:
        print(hit.payload, "score:", hit.score)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a neural search with a specified term.")
    parser.add_argument('search_term', type=str, help="The search term for the neural search")
    args = parser.parse_args()
    neural_search(args.search_term)
