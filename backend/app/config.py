from pydantic_settings import BaseSettings
from pathlib import Path
import os


class Settings(BaseSettings):
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    
    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k: int = 5
    relevance_threshold: float = 0.1
    
    pdf_dir: Path = Path("/app/documents")
    data_dir: Path = Path("/app/data")
    index_path: Path = Path("/app/data/index")
    
    class Config:
        env_file = None


settings = Settings()
