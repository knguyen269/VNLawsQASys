#Read file combined
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from sentence_transformers import SentenceTransformer
from pyvi.ViTokenizer import tokenize

path_data = "data/q_a.json"
batch_size = 128
index_name = "demo_simcsejson"
path_index = "config/index.json"
client = Elasticsearch([{'host': 'localhost', 'port': 9200}], timeout=50000)
model_embedding = SentenceTransformer('VoVanPhuc/sup-SimCSE-VietNamese-phobert-base')

def index_batch(docs):
    requests = []
    titles = [tokenize(doc["question"]) for doc in docs]
    title_vectors = embed_text(titles)
    for i, doc in enumerate(docs):
        request = doc
        request["_op_type"] = "index"
        request["_index"] = index_name
        request["title_vector"] = title_vectors[i]
        requests.append(request)
    bulk(client, requests)

def embed_text(batch_text):
    batch_embedding = model_embedding.encode(batch_text)
    return [vector.tolist() for vector in batch_embedding]

client.indices.delete(index=index_name, ignore=[404])
with open(path_index) as index_file:
    source = index_file.read().strip()
    client.indices.create(index=index_name, body=source)

docs = []
count = 0
df = pd.read_json(path_data).fillna(' ')
for index, row in df.iterrows():
    count += 1
    if row['Question'] != '' and row['Answer'] != '':
        item = {
            'id' : str(count), 
            'question': row['Question'],
            'answer': row['Answer']
        }
        docs.append(item)
        if count % batch_size == 0:
            index_batch(docs)
            docs = []
            print("Indexed {} documents.".format(count))
        #if count > 100:
        #    break
    else:
        print(row)
if docs:
    index_batch(docs)
    print("Indexed {} documents.".format(count))

print("Done Index")
client.indices.refresh(index=index_name)