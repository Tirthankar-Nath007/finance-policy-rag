from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    azure_openai_endpoint: str
    azure_openai_api_key: str
    
    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k: int = 5
    relevance_threshold: float = 0.1
    
    pdf_dir: Path = Path(__file__).parent.parent / "documents"
    data_dir: Path = Path(__file__).parent.parent / "data"
    index_path: Path = Path(__file__).parent.parent / "data" / "index.faiss"
    
    class Config:
        env_file = ".env"


settings = Settings()
