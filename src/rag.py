from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SimpleRAGIndex:
    """Small local retrieval layer for CRM notes and client documents."""

    def __init__(self, docs):
        self.docs = docs
        self.texts = [d["text"] for d in docs]
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(self.texts) if self.texts else None

    def search(self, query: str, client_id: str | None = None, top_k: int = 4):
        if not self.texts:
            return []
        candidates = list(range(len(self.docs)))
        if client_id:
            candidates = [i for i, d in enumerate(self.docs) if d.get("client_id") == client_id]
        if not candidates:
            return []
        query_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self.matrix[candidates]).flatten()
        ranked = sorted(zip(candidates, sims), key=lambda x: x[1], reverse=True)[:top_k]
        return [dict(self.docs[i], score=round(float(score), 3)) for i, score in ranked]


def build_rag_index(crm_notes, documents):
    docs = []
    for note in crm_notes:
        docs.append({
            "client_id": note["client_id"],
            "source": f"CRM Note {note['date']}",
            "title": "RM conversation note",
            "text": note["note"],
        })
    for doc in documents:
        docs.append({
            "client_id": doc["client_id"],
            "source": doc["doc_type"],
            "title": doc["title"],
            "text": doc["content"],
        })
    return SimpleRAGIndex(docs)
