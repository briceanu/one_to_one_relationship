from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy  import create_engine 


class Base(DeclarativeBase):
    ...

DATABASE_URL = 'sqlite:///databse.db'
engine = create_engine(DATABASE_URL,echo=True)

Session = sessionmaker(bind=engine, autocommit=False,autoflush=False)

def get_db():
    db = Session()
    try:
        yield db 
    finally:
        db.close()






