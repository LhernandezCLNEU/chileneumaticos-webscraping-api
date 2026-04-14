from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "chileneumaticos-api"
    SECRET_KEY: str = "please_change_me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    # Skip SSL verification for HTTP clients (development only)
    # Set to True by default for local dev convenience; override via .env in other environments
    SKIP_SSL_VERIFY: bool = True

    # Environment mode: 'development' or 'production'
    ENVIRONMENT: str = "development"

    MYSQL_HOST: str = "db"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "apiuser"
    MYSQL_PASSWORD: str = "apipassword"
    MYSQL_DB: str = "chileneumaticos"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    class Config:
        env_file = ".env"


settings = Settings()
