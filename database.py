from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.schemas import Base



DATABASE_URL = "postgresql://usermng:usermng123@localhost:5432/usermng"  

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def create_tables():
    Base.metadata.create_all(bind=engine)
        
        
