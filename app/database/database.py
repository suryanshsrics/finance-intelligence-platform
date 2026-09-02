from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.utils.settings import settings

# testing git connection

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=settings.database_user,
    port=settings.database_port,
    password=settings.database_password,
    host=settings.database_host,
    database=settings.database_name
)

# encode the url as '@' character in password is problemeatic

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()