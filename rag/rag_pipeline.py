import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class RAGContextRetriever:
    def __init__(self, documents, model_names):
        """
        Initialize with a list of document texts and an array of embedding model names.
        Each model will be used to generate embeddings, and a separate FAISS index will be created for each model.
        """
        self.documents = documents
        self.models = [SentenceTransformer(model_name) for model_name in model_names]
        self.indices = []
        self.embeddings = []
        self.build_indices()

    def build_indices(self):
        """
        For each embedding model, generate embeddings for the documents and create a FAISS index.
        """
        for model in self.models:
            # Generate embeddings for documents
            embeddings = model.encode(self.documents, convert_to_tensor=False)
            embeddings = np.array(embeddings).astype("float32")

            # Create a FAISS index and add embeddings
            index = faiss.IndexFlatL2(embeddings.shape[1])
            index.add(embeddings)

            # Store embeddings and index for later retrieval
            self.indices.append(index)
            self.embeddings.append(embeddings)

    def retrieve_context(self, query, top_k=5):
        """
        Given a query, retrieve the most relevant context from the documents using the best-performing model.
        The model with the highest average similarity score is selected dynamically for each query.
        """
        best_retrieval = None
        best_score = -float('inf')

        for i, model in enumerate(self.models):
            # Encode query with the current model
            query_embedding = model.encode([query], convert_to_tensor=False).astype("float32")

            # Search the corresponding FAISS index
            distances, indices = self.indices[i].search(query_embedding, top_k)

            # Calculate average score for this model (using negative distances since FAISS returns L2 distances)
            avg_score = -np.mean(distances)

            # If this model performs better, update best retrieval results
            if avg_score > best_score:
                best_score = avg_score
                best_retrieval = [self.documents[idx] for idx in indices[0]]

        # Join relevant documents as a single context string for generation input
        return " ".join(best_retrieval)


# Step 1: Define the embedding models to use and prepare the documents
model_names = [
    "all-MiniLM-L6-v2",  # Fast, compact embedding model
    "multi-qa-MiniLM-L6-cos-v1",  # Optimized for question answering
    "all-mpnet-base-v2"  # Balanced model with good semantic understanding
]
documents = [
    "Requirement 1: The system shall support user authentication via OAuth.",
    "Requirement 2: The application must log user activity for audit purposes.",
    "Requirement 3: Data encryption must be applied to all user data stored on the server.",
    # Additional documents as needed...
]

# Step 2: Initialize RAG context retriever with multiple embedding models
rag_retriever = RAGContextRetriever(documents, model_names)


# Step 3: Retrieve Context for Generative Model
def get_context_for_generation(requirement_text):
    context = rag_retriever.retrieve_context(requirement_text)
    return context


# Example usage
requirement_text = "Generate a test plan for user authentication and data encryption."
context = get_context_for_generation(requirement_text)

print("Retrieved Context for Generation:")
print(context)

# The `context` can now be used as input to a generative model
