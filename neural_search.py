from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer
import argparse
import time


encoder = SentenceTransformer("all-MiniLM-L6-v2")
qdrant = QdrantClient("http://localhost:6333")

def neural_search(query):
    print(f"Running neural search with term: {query}")

    start_time = time.time()

    hits = qdrant.search(
        collection_name="zalando",
        query_vector=encoder.encode(query).tolist(),
        limit=3,
    )

    end_time = time.time()

    for hit in hits:
        print(hit.payload, "score:", hit.score)

    # Calculate and print the response time in milliseconds
    response_time_ms = (end_time - start_time) * 1000
    print(f"Response time: {response_time_ms:.2f} ms")
    
if __name__ == "__main__":
    print("Neural search service. Type 'exit' to stop.")
    while True:
        try:
            query = input("Enter search term: ")
            if query.lower() == 'exit':
                print("Exiting neural search service.")
                break
            neural_search(query)
        except KeyboardInterrupt:
            print("\nDetected Ctrl+C, exiting neural search service.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")