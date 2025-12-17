# agents/TechnicalAgent/technical_agent.py

import os
import pandas as pd
import numpy as np
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------------------------------
# Path Resolution (absolute, safe)
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "EY_dataset.csv")
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "sku_embeddings.npy")

# -------------------------------------------------
# OpenAI Client
# -------------------------------------------------
client = OpenAI()

# -------------------------------------------------
# Internal cache (loaded once per process)
# -------------------------------------------------
_DF_CACHE = None


# -------------------------------------------------
# Embedding utility
# -------------------------------------------------
def _get_embedding(text: str) -> list:
    """
    Generate embedding using OpenAI embedding model
    """
    text = text.replace("\n", " ").strip()
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return response.data[0].embedding


# -------------------------------------------------
# Dataset + embedding loader
# -------------------------------------------------
def _load_dataset() -> pd.DataFrame:
    """
    Loads SKU dataset and embeddings once (lazy loading).
    """
    global _DF_CACHE

    if _DF_CACHE is not None:
        return _DF_CACHE

    df = pd.read_csv(DATASET_PATH)

    # Build descriptive text for each SKU
    df["description"] = (
        df["Product Category"].astype(str) + " " +
        df["Cable Type"].astype(str) + " " +
        df["Voltage Grade"].astype(str) + " " +
        df["Conductor Material"].astype(str) + " " +
        df["Core Count"].astype(str) + " core " +
        df["Cross Section (sq.mm)"].astype(str) + " sqmm " +
        df["Armouring"].astype(str) + " " +
        df["Insulation Type"].astype(str) + " " +
        df["Standard"].astype(str)
    )

    # Load or generate embeddings
    if not os.path.exists(EMBEDDINGS_PATH):
        print("🔄 Generating SKU embeddings (one-time)...")
        df["embedding"] = df["description"].apply(_get_embedding)
        np.save(EMBEDDINGS_PATH, np.stack(df["embedding"].values))
    else:
        print("✅ Loading cached SKU embeddings...")
        df["embedding"] = list(np.load(EMBEDDINGS_PATH, allow_pickle=True))

    _DF_CACHE = df
    return df


# -------------------------------------------------
# Core matching logic
# -------------------------------------------------
def _match_tender_to_skus(
    df: pd.DataFrame,
    tender_text: str,
    top_n: int
) -> list:
    """
    Matches tender input against SKU embeddings and returns top N matches.
    """
    tender_embedding = np.array(_get_embedding(tender_text))
    sku_embeddings = np.stack(df["embedding"].values)

    similarities = cosine_similarity(
        tender_embedding.reshape(1, -1),
        sku_embeddings
    )[0]

    df = df.copy()
    df["confidence"] = (similarities * 100).round(2)

    top_df = df.nlargest(top_n, "confidence")[[
        "Product Category",
        "Cable Type",
        "Voltage Grade",
        "Conductor Material",
        "Core Count",
        "Cross Section (sq.mm)",
        "Armouring",
        "Insulation Type",
        "Standard",
        "Price (Rupees/m)",
        "confidence"
    ]]

    return top_df.to_dict(orient="records")


# -------------------------------------------------
# PUBLIC AGENT ENTRY POINT
# -------------------------------------------------
def run_technical_agent(
    tender_input_line: str,
    top_n: int = 3
) -> dict:
    """
    Technical Agent entry point.
    """
    df = _load_dataset()
    matches = _match_tender_to_skus(df, tender_input_line, top_n)

    return {
        "tender_input": tender_input_line,
        "top_matches": matches
    }


# -------------------------------------------------
# Local test (safe to remove later)
# -------------------------------------------------
if __name__ == "__main__":
    test_input = (
        "4 core 185 sqmm copper armoured cable "
        "galvanized steel PVC sheathed as per IS 7098"
    )
    from pprint import pprint
    pprint(run_technical_agent(test_input))
