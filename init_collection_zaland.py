from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer
import json
import psycopg2
import time
import sys
import signal


encoder = SentenceTransformer("all-MiniLM-L6-v2")
qdrant = QdrantClient(":memory:")

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)


def fetch_blog_posts(cur):
    cur.execute("SELECT id, title, summary, tags, content FROM post_content")
    blog_posts = cur.fetchall()
    # cur.close()
    # conn.close()
    return blog_posts

def connect_db():
    return psycopg2.connect(dbname="zalando", user="postgres",password="101701",host="localhost")



def upload_embedding(blog_posts):
    qdrant.recreate_collection(
    collection_name="zalando",
    vectors_config=models.VectorParams(
        size=encoder.get_sentence_embedding_dimension(),  # Vector size is defined by used model
        distance=models.Distance.COSINE,
        ),
    )


    qdrant.upload_records(
        collection_name="zalando",
        records=[
            models.Record(
                id=entry[0], vector=encoder.encode(entry[4]).tolist(), payload={
                    "id" : entry[0],
                    "title" : entry[1],
                    "summary": entry[2],
                    "tags": entry[3]
                }
            )
            for idx, entry in enumerate(blog_posts)
        ],
    )
    print("finished uploading embeddings!")


    
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    print("Service started. Press Ctrl+C to stop.")

    conn = connect_db()
    cur = conn.cursor()
    blog_posts = fetch_blog_posts(cur)
    upload_embedding(blog_posts)
    while True:
        # Here, you can wait for an event, check for new data, or simply pass.
        # This example does nothing and just keeps the service alive.
        pass