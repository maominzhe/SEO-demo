from diagrams import Cluster, Diagram, Edge
from diagrams.generic.blank import Blank
from diagrams.generic.os import Windows
from diagrams.onprem.analytics import Spark
from diagrams.onprem.client import User
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.monitoring import Grafana
from diagrams.onprem.network import Nginx
from diagrams.onprem.queue import Kafka
from diagrams.programming.flowchart import Database
from diagrams.custom import Custom

with Diagram("SEO Performance Workflow", show=False, direction="TB"):
    user = User("User")
    google = Blank("Google")
    crawler = Nginx("Crawler")
    scheduler = Kafka("Scheduler")
    repo = Database("Page Repository")
    parser = Redis("Parser")
    indexer = PostgreSQL("Indexer")
    engine = Spark("Query Engine")
    ranking = Grafana("Ranking")
    ranked_pages = Windows("Ranked Pages")
    feedback = Blank("Feedback")

    user >> google >> engine >> ranking >> ranked_pages >> feedback >> engine
    ranked_pages >> user
    google >> crawler >> repo >> parser >> indexer >> ranking
    scheduler >> crawler
    repo >> Edge(style="dashed") >> scheduler
