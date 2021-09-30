from pydantic import BaseSettings


class NonebugCofig(BaseSettings):
    nonebug_log_level: str = "DEBUG"
    nonebug_log_dir: str = "nonebug_logs"
    class Config:
        extra = "ignore"