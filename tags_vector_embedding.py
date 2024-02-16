#from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer
import json
import psycopg2


encoder = SentenceTransformer("all-MiniLM-L6-v2")

def connect_db():
    return psycopg2.connect(dbname="zalando", user="postgres",password="101701",host="localhost")

def create_table_if_not_exists(conn, cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tag_vector_embeddings (
            id SERIAL PRIMARY KEY,
            blog_post_id INTEGER,
            vector FLOAT8[],
            CONSTRAINT fk_vector_blog_post FOREIGN KEY (blog_post_id)
            REFERENCES blog_posts (id) ON DELETE CASCADE
        );
    """)
    conn.commit()

def encode_tags_and_save_vector(conn,cur):


    # 从post_content表中读取数据
    cur.execute("SELECT blog_post_id, title FROM post_content")

    for record in cur.fetchall():
        blog_post_id, tags = record
        # 对标题进行编码
        vector = encoder.encode(tags).tolist()

        # 将向量写入vector_embeddings表
        cur.execute(
            "INSERT INTO content_vector_embeddings (blog_post_id, vector) VALUES (%s, %s)",
            (blog_post_id, vector)
        )

        print(f"writing embedded vector with post_id {blog_post_id}")

    # 提交事务
    conn.commit()

    # # 关闭连接
    # cur.close()
    # conn.close()

if __name__ == "__main__":
    conn = connect_db()
    cur = conn.cursor()
    create_table_if_not_exists(conn,cur)
    encode_tags_and_save_vector(conn,cur)
    cur.close()
    conn.close()