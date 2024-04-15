import time
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from pyvi.ViTokenizer import tokenize


def load_es():
    model_embedding = SentenceTransformer(
        'VoVanPhuc/sup-SimCSE-VietNamese-phobert-base')
    client = Elasticsearch()
    return model_embedding, client


def search(query):

    def embed_text(text):
        text_embedding = model_embedding.encode(text)
        return text_embedding.tolist()

    model_embedding, client = load_es()
    time_embed = time.time()
    query_vector = embed_text([tokenize(query)])[0]
    print(len(query_vector))
    print('TIME EMBEDDING ', time.time() - time_embed)
    script_query = {
        "script_score": {
            "query": {
                "match_all": {}
            },
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'title_vector') + 1.0",
                "params": {"query_vector": query_vector}
            }
        }
    }



    response = client.search(
        index='demo_simcsejson',
        body={
            "size": 10,
            "query": script_query,
            "_source": {
                "includes": ["id", "question", "answer"]
            },
        },
        ignore=[400]
    )

    result = []
    id_rs = 0
    for hit in response["hits"]["hits"]:
        id_rs += 1
        result.append([id_rs, hit["_source"]['question'],
                      hit["_source"]['answer']])
    return result
