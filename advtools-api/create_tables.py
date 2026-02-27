from sqlalchemy import create_engine
from models import Base
import models

DATABASE_URL = "postgresql://postgres:0000@localhost:5432/advtools"
sync_engine = create_engine(DATABASE_URL)

def create_new_tables():
    print("Creating new tables...")
    Base.metadata.create_all(bind=sync_engine)
    print("Done!")

if __name__ == "__main__":
    create_new_tables()
