import json
import os
import pickle

import pandas as pd
import numpy as np
import psycopg2
import umap
from sklearn import preprocessing

import matplotlib.pyplot as plt
import seaborn as sns


class DmReduction:

    def __init__(self, load_from=None):
        if load_from and os.path.exists(load_from):
            self.mapper = pickle.load(open(load_from, "rb"))
        else:
            self.mapper = umap.UMAP(
                n_neighbors=5,
                n_components=2,
                metric="cosine",
                output_metric="euclidean",
                repulsion_strength=2.0,
                min_dist=0.5,
            )

    def save(self, path):
        pickle.dump(self.mapper, open(path, "wb"))


def load_db_embeddings():
    print("loading embeddings from database..")
    # Connect to your database
    conn = psycopg2.connect(
        dbname="zalando", user="postgres", password="101701", host="localhost"
    )

    # Create a cursor object
    cur = conn.cursor()

    # Fetch content vector embeddings
    cur.execute(
        """
        SELECT blog_post_id, vector
        FROM content_vector_embeddings
    """
    )
    content_embeddings = cur.fetchall()

    # Assuming there's a table for tags where each blog post ID is associated with a tag
    cur.execute(
        """
        SELECT blog_post_id, tags
        FROM post_content
    """
    )
    tags = cur.fetchall()

    # Close the cursor and connection
    cur.close()
    conn.close()

    print("finished loading embeddings, closing database connection..")

    # Process fetched data
    embeddings = np.array([row[1] for row in content_embeddings])
    blog_post_ids = [row[0] for row in content_embeddings]
    tags_dict = {row[0]: row[1] for row in tags}
    labels = np.array([tags_dict[id] for id in blog_post_ids])
    return embeddings, blog_post_ids, tags_dict, labels


def visualize_embeddings(reduced_embeddings, labels):
    # Unique labels for coloring
    unique_labels = np.unique(labels)
    palette = sns.color_palette("hsv", len(unique_labels))
    label_to_color = {label: palette[i] for i, label in enumerate(unique_labels)}

    # Plotting
    colors = [label_to_color[label] for label in labels]
    plt.figure(figsize=(12, 10))  # Increased figure size for better visibility
    plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], c=colors, alpha=0.5)
    plt.title("UMAP Projection of Content Vector Embeddings")
    plt.xlabel('UMAP-1')
    plt.ylabel('UMAP-2')

    # Creating a legend
    handles = [plt.Line2D([0], [0], marker='o', color='w', label=label,
                        markerfacecolor=color, markersize=10) for label, color in label_to_color.items()]
    legend = plt.legend(title='Tags', handles=handles, bbox_to_anchor=(1.05, 1), loc='upper left')

    # Adjust layout
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust the rect parameter as needed

    # Save the figure to the current directory
    plt.savefig('umap_projection.png', bbox_inches='tight')  # Saves the plot as 'umap_projection.png'

    plt.show()  # Show the plot as the last step


if __name__ == "__main__":
    embeddings, blog_post_ids, tags_dict, labels = load_db_embeddings()
    # dm_reduction = DmReduction()
    reducer = umap.UMAP(
        n_neighbors=5,
        n_components=2,
        metric="cosine",
        output_metric="euclidean",
        repulsion_strength=2.0,
        min_dist=0.5,
    )
    #reduced_embeddings = dm_reduction.fit_transform(embeddings)
    reduced_embeddings = reducer.fit_transform(embeddings)
    visualize_embeddings(reduced_embeddings, labels)
