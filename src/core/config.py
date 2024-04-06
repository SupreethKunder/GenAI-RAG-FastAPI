from pydantic_settings import BaseSettings, SettingsConfigDict
import warnings
import importlib.metadata

try:
    current_version = importlib.metadata.version("genai-rag-semantic-movies")
except Exception:
    current_version = "0.0.0"
warnings.filterwarnings("ignore", category=DeprecationWarning)


# The class `Settings` defines various configuration settings for a project with default values and a
# configuration dictionary.
class Settings(BaseSettings):
    PROJECT_NAME: str = "GenAI RAG Semantic Movies"
    API_VERSION: str = current_version
    KMONGO_URL: str
    HUGGINGFACE_API_KEY: str
    REDIS_URL: str
    BASE_URL: str = "0.0.0.0"
    AUTH0_DOMAIN: str
    AUTH0_CLIENT_ID: str
    AUTH0_CLIENT_SECRET: str

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )


settings = Settings()
