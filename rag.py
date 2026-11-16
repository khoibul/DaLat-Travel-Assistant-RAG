
import json
import os

import numpy as np
import requests
import streamlit as st

from dotenv import load_dotenv


# -----------------------------------
# 1. Configuration
# -----------------------------------

load_dotenv()

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
).rstrip("/")

EMBEDDING_MODEL = "embeddinggemma"
CHAT_MODEL = "qwen3:4b"

KNOWLEDGE_BASE_PATH = "knowledge_base.json"

TOP_K = 3


# -----------------------------------
# 2. Load knowledge base
# -----------------------------------

def load_knowledge_base():

    with open(
        KNOWLEDGE_BASE_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return data


# -----------------------------------
# 3. Generate embeddings
# -----------------------------------

def get_embeddings(texts):

    url = f"{OLLAMA_BASE_URL}/api/embed"

    payload = {
        "model": EMBEDDING_MODEL,
        "input": texts
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        return np.array(
            result["embeddings"],
            dtype=np.float32
        )

    except requests.exceptions.RequestException as error:

        raise ConnectionError(
            f"Could not connect to Ollama embedding API: {error}"
        )

    except (KeyError, ValueError) as error:

        raise RuntimeError(
            f"Invalid embedding response: {error}"
        )


# -----------------------------------
# 4. Cache knowledge base embeddings
# -----------------------------------

@st.cache_resource(show_spinner="Loading travel guide and generating embeddings...")

def load_guide_embeddings():

    entries = load_knowledge_base()

    texts = [
        f"{entry['title']}. {entry['text']}"
        for entry in entries
    ]

    embeddings = get_embeddings(texts)

    return entries, embeddings


# -----------------------------------
# 5. Calculate cosine similarity
# -----------------------------------

def cosine_similarity(vector_a, vector_b):

    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(
        np.dot(vector_a, vector_b) /
        (norm_a * norm_b)
    )


# -----------------------------------
# 6. Retrieve top-k entries
# -----------------------------------

def retrieve_entries(
    question,
    entries,
    guide_embeddings,
    top_k=TOP_K
):

    query_embedding = get_embeddings([question])[0]

    scores = []

    for index, entry in enumerate(entries):

        score = cosine_similarity(
            query_embedding,
            guide_embeddings[index]
        )

        scores.append({
            "entry": entry,
            "score": score
        })

    scores.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return scores[:top_k]



# -----------------------------------
# 7. Generate answer with Qwen3
# -----------------------------------

def generate_answer(question, retrieved_results):

    context = ""

    for item in retrieved_results:
        entry = item["entry"]

        context += (
            f"[{entry['id']}] {entry['title']}\n"
            f"{entry['text']}\n\n"
        )

    prompt = f"""
You are a travel assistant for Da Lat.

Answer the user's question using ONLY the information
provided in the travel guide context below.

Rules:
1. Do not use outside knowledge.
2. Do not invent facts, prices, or opening hours.
3. Cite the entry IDs used in your answer, such as [G09].
4. If the context does not contain enough information
   to answer the question, reply exactly:
   "I don't know."
5. Keep the answer clear and concise.

Travel Guide Context:
{context}

User Question:
{question}

Answer:
"""

    url = f"{OLLAMA_BASE_URL}/api/chat"

    payload = {
        "model": CHAT_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "think": False
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=180
        )

        response.raise_for_status()

        result = response.json()

        answer = result["message"]["content"].strip()

        # Remove Qwen3 thinking content
        if "</think>" in answer:
            answer = answer.split("</think>", 1)[1].strip()

        return answer

    except requests.exceptions.RequestException as error:

        raise ConnectionError(
            f"Could not connect to Ollama chat API: {error}"
        )

    except (KeyError, ValueError) as error:

        raise RuntimeError(
            f"Invalid Ollama chat response: {error}"
        )
