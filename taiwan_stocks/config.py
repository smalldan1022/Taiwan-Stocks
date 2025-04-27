import os

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class DBConfig(BaseModel):
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "3306"))
    user: str = os.getenv("DB_USER", "root")
    password: str = os.getenv("DB_PASSWORD", "")
    database: str = os.getenv("DB_NAME", "taiwan_stocks")

    @property
    def parameters(self) -> dict:
        return self.model_dump()

    @property
    def url(self):
        return (
            f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        )
