import tweepy
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

# Replace with your Bearer Token
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAH4q0QEAAAAAERfmMpI5VXNQlbTXol6lhnTb0vo%3DouVmBf4yIQeJLxPsoUUP8QQDzExCS8VwcyfkbYmCRLaOhqNSG5'
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Search recent tweets with the hashtag
query = "#ClimateAction -is:retweet"
tweets = tweepy.Paginator(
    client.search_recent_tweets,
    query=query,
    tweet_fields=["author_id", "created_at", "referenced_tweets"],
    max_results=100
).flatten(limit=50)

edges = []
users = {}

for tweet in tweets:
    user_id = str(tweet.author_id)
    users[user_id] = users.get(user_id, 0) + 1

    if tweet.referenced_tweets:
        for ref in tweet.referenced_tweets:
            if ref.type in ['retweeted', 'replied_to']:
                source = user_id
                target = str(ref.id)
                edges.append((source, target))

G = nx.DiGraph()
G.add_edges_from(edges)

# Save node and edge data
pd.DataFrame(list(G.nodes()), columns=["user_id"]).to_csv("nodes.csv", index=False)
pd.DataFrame(edges, columns=["source", "target"]).to_csv("edges.csv", index=False)

# Analyze graph
in_degree = dict(G.in_degree())
pagerank = nx.pagerank(G)
betweenness = nx.betweenness_centrality(G)

top_users = pd.DataFrame({
    "user_id": list(in_degree.keys()),
    "in_degree": [in_degree.get(u, 0) for u in in_degree.keys()],
    "pagerank": [pagerank.get(u, 0) for u in in_degree.keys()],
    "betweenness": [betweenness.get(u, 0) for u in in_degree.keys()]
}).sort_values(by="pagerank", ascending=False)

top_users.to_csv("top_users.csv", index=False)

# Visualize graph
plt.figure(figsize=(10, 7))
pos = nx.spring_layout(G)
sizes = [in_degree.get(n, 1) * 100 for n in G.nodes()]
nx.draw_networkx_nodes(G, pos, node_size=sizes, alpha=0.7)
nx.draw_networkx_edges(G, pos, alpha=0.3)
plt.title("Twitter Interaction Graph (#ClimateAction)")
plt.axis("off")
plt.savefig("network_graph.png")
plt.show()

import time

# Inside your loop (just before or after each request)
time.sleep(1)  # Wait 1 second between requests
