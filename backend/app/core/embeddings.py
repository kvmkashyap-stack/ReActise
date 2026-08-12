from langchain_huggingface import HuggingFaceEmbeddings

# Local Hugging Face embeddings (matches the 384 vector dimension in Supabase)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)