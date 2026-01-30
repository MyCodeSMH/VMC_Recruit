import os
import re
import numpy as np
from openai import OpenAI


class DocumentRanker:
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        self.documents = []
        self.filenames = []
        self.emails = []
        self.embeddings = None
        self.client = OpenAI()

    def extract_email(self, text: str):
        match = re.search(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            text
        )
        return match.group(0) if match else None

    def load_documents(self):
        for root, _, files in os.walk(self.folder_path):
            for filename in files:
                if filename.endswith(".txt"):
                    path = os.path.join(root, filename)
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read().strip()

                    if not text:
                        continue

                    self.documents.append(text)
                    self.filenames.append(path)
                    self.emails.append(self.extract_email(text))

        print(f"Loaded {len(self.documents)} documents.")

    def vectorize_documents(self):
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=self.documents
        )

        # Use float64 for numerical safety
        X = np.array([e.embedding for e in response.data], dtype=np.float64)
    
        # Replace NaN / Inf
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

        norms = np.linalg.norm(X, axis=1, keepdims=True)

        # Remove zero vectors
        mask = norms.squeeze() > 1e-6
        X = X[mask]

        self.filenames = [f for f, m in zip(self.filenames, mask) if m]
        self.emails = [e for e, m in zip(self.emails, mask) if m]

        # Normalize
        self.embeddings = X / norms[mask]

        print(f"Embeddings created ({len(self.embeddings)} valid vectors).")

    def rank(self, query: str):
        q_embedding = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        ).data[0].embedding

        q = np.array(q_embedding, dtype=np.float64)
        q = np.nan_to_num(q, nan=0.0, posinf=0.0, neginf=0.0)

        q_norm = np.linalg.norm(q)
        if q_norm < 1e-6:
            raise ValueError("Query embedding invalid")

        q /= q_norm

        # Safe cosine similarity
        similarities = np.clip(self.embeddings @ q, -1.0, 1.0)

        results = []
        for file, email, score in zip(self.filenames, self.emails, similarities):
            if score >= 0.45:
                label = "RELEVANT"
            elif score >= 0.25:
                label = "POSSIBLY RELEVANT"
            else:
                label = "NOT RELEVANT"

            results.append((file, email, float(score), label))

        results.sort(key=lambda x: x[2], reverse=True)
        return results


if __name__ == "__main__":
    folder = "resumes"  # <-- your folder
    ranker = DocumentRanker(folder)

    ranker.load_documents()
    ranker.vectorize_documents()

    while True:
        query = input("\nEnter job description (or 'exit'): ")
        if query.lower() == "exit":
            break

        results = ranker.rank(query)

        print("\nResume Ranking:\n")
        for file, email, score, label in results:
            email = email if email else "Email not found"
            print(f"{label:<18} | {score:.4f} | {email} | {file}")
