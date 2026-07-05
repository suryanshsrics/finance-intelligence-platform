from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# DATABASE_URL = "postgresql://postgres:Suryansh@0912@localhost:5432/finance_intelligence"

# encode the url as '@' character in password is problemeatic
DATABASE_URL = "postgresql+psycopg://postgres:Suryansh%400912@localhost:5432/finance_intelligence"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()