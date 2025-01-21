import sqlalchemy as sql
import sqlalchemy.ext.declarative as declarative
import sqlalchemy.orm as orm

DATABASE_URL = "mysql+pymysql://etech:jPjuI2i1h334@192.168.105.61/indigo"


engine = sql.create_engine(DATABASE_URL)

SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative.declarative_base()



def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()