from ..database.connect import client
from ..core.config import settings
import requests
from typing import List, Dict, Union, Optional
from bson.json_util import dumps
import json

db = client.sample_mflix
collection = db.movies

embedding_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"


def generate_embedding(text: str) -> List[float]:
    response = requests.post(
        embedding_url,
        headers={"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"},
        json={"inputs": text},
    )

    if response.status_code != 200:
        raise ValueError(
            f"Request failed with status code {response.status_code}: {response.text}"
        )

    return response.json()


def persist_vectors_to_db() -> List[Optional[str]]:
    for doc in collection.find({"plot": {"$exists": True}}).limit(50):
        doc["plot_embedding_hf"] = generate_embedding(doc["plot"])
        collection.replace_one({"_id": doc["_id"]}, doc)
    return []


def perform_vector_search(query: str) -> List[Dict[str, Union[float, int, str]]]:
    cursor_results = collection.aggregate(
        [
            {
                "$vectorSearch": {
                    "queryVector": generate_embedding(query),
                    "path": "plot_embedding_hf",
                    "numCandidates": 100,
                    "limit": 4,
                    "index": "PlotSemanticSearch",
                }
            },
            {"$project": {"title": 1, "plot": 1}},
        ]
    )
    return json.loads(dumps(cursor_results))


# for document in results:
#     print(f'Movie Name: {document["title"]},\nMovie Plot: {document["plot"]}\n')
