import requests
from bs4 import BeautifulSoup
import psycopg2
import time
import re

# Database connection parameters
dbname = 'zalando'
user = 'postgres'
password = '101701'
host = 'localhost'
base_url = 'https://engineering.zalando.com/'
element_list = ['p', 'li', 'ol', 'h3', 'h4', 'h5', 'h6']

# Connect to PostgreSQL
def create_db_if_not_exists():
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
    cur = conn.cursor()

    # Create a table for storing blog posts if it doesn't already exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS post_content (
            id SERIAL PRIMARY KEY,
            blog_post_id INTEGER,
            title TEXT,
            summary TEXT,
            tags TEXT,
            content TEXT,
            CONSTRAINT fk_blog_post FOREIGN KEY (blog_post_id)
            REFERENCES blog_posts (id) ON DELETE CASCADE
        );
    """)
    conn.commit()

    cur.close()
    conn.close()


def connect_db():
    return psycopg2.connect(dbname="zalando", user="postgres",password="101701",host="localhost")

def fetch_blog_posts():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, content_url FROM blog_posts")
    blog_posts = cur.fetchall()
    cur.close()
    conn.close()
    return blog_posts

def scrape_and_store_content(blog_post_id, url, conn, cur):
    response = requests.get(url)
    try:
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            first_content_post = soup.find('article', class_='content-post')
            if first_content_post:
                title = first_content_post.find('header', class_='post-header').h1.text.strip()
                try:
                    summary = first_content_post.find('div','summary').p.text.strip()
                except AttributeError:
                    summary = ''

                try:
                    tags = first_content_post.find('div','meta').find('div','tags').find('div','taglist').text.strip()
                except AttributeError:
                    tags = ''

                content=''
                blogpost_wysiwyg = first_content_post.find('div','blogpost wysiwyg')
                for element in blogpost_wysiwyg.descendants:
                    if element.name in element_list:
                        content += '\n\n' + ''.join(element.find_all(string=True, recursive=False)).strip()
                    elif element.name == None :
                        content += element.strip()
                    elif element.name == 'code':
                        content += element.get_text().strip()
            

            cur.execute("INSERT INTO post_content (blog_post_id, title, summary, tags, content)\
                        VALUES (%s, %s, %s, %s, %s)", (blog_post_id, title, summary, tags, content))
            conn.commit()
            print(f"Inserting post: {blog_post_id}")

            
    except Exception as e:
        print(f"An error occurred: {e}")


        


if __name__ == "__main__":
    # test_url = "https://engineering.zalando.com/posts/2023/07/rendering-engine-tales-road-to-concurrent-react.html"
    # scrape_and_store_content(1,test_url)
    create_db_if_not_exists()
    blog_posts = fetch_blog_posts()
    conn = connect_db()
    cur = conn.cursor()
    for blog_post_id, content_url in blog_posts:
        scrape_and_store_content(blog_post_id, content_url, conn, cur)
        time.sleep(1)
    cur.close()
    conn.close()