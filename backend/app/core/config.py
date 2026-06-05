from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "VCC Platform"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/vcc_platform"
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Analysis services (validation + analysis)
    ANALYSIS_CHESS_URL: str = "http://analysis-chess:8001"
    ANALYSIS_XIANGQI_URL: str = "http://analysis-xiangqi:8002"
    ANALYSIS_GO_URL: str = "http://analysis-go:8003"
    ANALYSIS_GOMOKU_URL: str = "http://analysis-gomoku:8004"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
