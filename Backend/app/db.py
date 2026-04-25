import os
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

# In Railway the container WORKDIR is /app and data is at /app/data.
# Locally it resolves to Backend/data. Both work with this logic.
_default_data_dir = Path(__file__).resolve().parents[1] / "data"
DATA_DIR = Path(os.getenv("DATA_DIR", str(_default_data_dir)))
DATA_DIR.mkdir(parents=True, exist_ok=True)

(DATA_DIR / "uploads").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "reports").mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATA_DIR / "career_os.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH.as_posix()}")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
