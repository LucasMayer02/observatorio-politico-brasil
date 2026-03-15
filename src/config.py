from dotenv import load_dotenv
import os

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Observatorio Politico Brasil")
ENV = os.getenv("ENV", "development")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")

CHROMA_DIR = os.getenv("CHROMA_DIR", "./data/chroma")
RAW_DATA_DIR = os.getenv("RAW_DATA_DIR", "./data/raw")
PROCESSED_DATA_DIR = os.getenv("PROCESSED_DATA_DIR", "./data/processed")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))