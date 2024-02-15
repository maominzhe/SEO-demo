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

# Connect to PostgreSQL
conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
cur = conn.cursor()

# Create a table for storing blog posts if it doesn't already exist
cur.execute("""
    CREATE TABLE IF NOT EXISTS blog_posts (
        id SERIAL PRIMARY KEY,
        title TEXT,
        preview TEXT,
        content_url TEXT
    );
""")
conn.commit()

def is_valid_url(url):
    """Check if the URL does not point to a disallowed /drafts/ path."""
    return '/drafts/' not in url

def fetch_blog_posts(url):
    """Function to fetch and store blog content, skipping resources under /drafts/"""
    headers = {
        'User-Agent': 'personal learning purpose'
    }
    print(f"Processing URL: {url}")
    if not is_valid_url(url):
        print(f"Skipping URL due to disallowed path: {url}")
        return
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Received response for {url} with status code: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            posts = soup.find_all('article', class_='article')
            
            for post in posts:
                title = post.find('h1', class_='title').text.strip()
                preview = post.find('p', class_='preview').text.strip()
                content_url = post.find('a')['href']
                full_url = base_url + content_url[2:] if content_url.startswith('./') else content_url

                
                
                print(f"Inserting post: {title}")
                cur.execute("INSERT INTO blog_posts (title, preview,content_url) VALUES (%s, %s, %s)", (title, preview,full_url))
                conn.commit()
                print("Insert successful")
                
                # Delay between requests to reduce load on server
                time.sleep(1)
            
            # return if theres a next page
            next_page_link = soup.find('a', {'class': 'no-border'})
            if next_page_link is not None:
                return base_url + next_page_link['href'][2:]
            else:
                return False
        else:
            print(f"Failed to fetch data from {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")


has_next_page = True
first_page = 'index.html'
next_page = base_url + first_page

while next_page:
    # The homepage URL of the blog you want to scrape
    print(f"Fetching articles from: {next_page}")
    next_page = fetch_blog_posts(next_page)

# Close database connection
cur.close()
conn.close()