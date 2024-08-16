from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    version: str = Field("alpha")
    # LLM general settings
    llm_api_max_retry: int = Field(3, description="Max retry count for making API calls to LLM")
    llm_timeout: int = Field(60, description="time to wait before terminating the connection")
    llm_temperature: int = Field(0, description="temperature, the lower value the more deterministic")
    llm_max_tokens: int = Field(8192, description="max number of tokens to limit the context size")

    # chatGPT specific settings
    openai_api_key: str = Field(os.getenv("OPENAI_API_KEY", ""), description="OPENAI API key")
    openai_model: str = Field(os.getenv("OPENAI_MODEL", ""), description="OpenAI model to be used")
    use_demo_key: bool = Field(True, description="whether to use demo key")
    # ANTHROPIC_API_KEY: str = Field(os.getenv("ANTHROPIC_API_KEY"), description="ANTHROPIC API key")
    # pinecone_api_key: str = Field(os.getenv("PINECONE_API_KEY"), description="Pinecone API key")

    demo_mode: bool = Field(False, description="whether to enable demo mode")
    # Database settings
    # DB_HOST: str = Field(..., description="Database host")
    # DB_PORT: int = Field(5432, description="Database port")
    # DB_NAME: str = Field(..., description="Database name")
    # DB_USER: str = Field(..., description="Database username")
    # DB_PASSWORD: str = Field(..., description="Database password")

    debug: bool = Field(False, description="Debug mode")
    log_level: str = Field("INFO", description="Logging level")
    log_format: str = Field("<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | <cyan>{file}</cyan> | <level>{message}</level>", description="logging format")

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Create an instance of the Settings class
@lru_cache()
def get_settings() -> Settings:
    """cache settings so we only load it once"""
    return Settings()