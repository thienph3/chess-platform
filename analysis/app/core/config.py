from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "VCC Analysis Service"
    DEBUG: bool = False

    # Engine binary paths
    STOCKFISH_PATH: str = "/usr/local/bin/stockfish"
    PIKAFISH_PATH: str = "/usr/local/bin/pikafish"
    KATAGO_PATH: str = "/usr/local/bin/katago"
    KATAGO_MODEL_PATH: str = "/usr/local/share/katago/model.bin.gz"
    KATAGO_CONFIG_PATH: str = "/usr/local/share/katago/config.cfg"

    # Analysis defaults
    DEFAULT_DEPTH: int = 20
    MAX_DEPTH: int = 30
    DEFAULT_NUM_VARIATIONS: int = 3
    ENGINE_TIMEOUT: int = 30  # seconds

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
