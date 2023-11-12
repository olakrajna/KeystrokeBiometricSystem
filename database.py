from sqlalchemy import create_engine, ForeignKey, Column, String, Integer
from  sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import bcrypt

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True)
    password_hash = Column(String)
    time = Column(String)

    def set_password(self, password):
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        self.password_hash = password_hash.decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def __init__(self, username, password_hash, time):
        self.username = username
        self.password_hash = password_hash
        self.time = time

    def __repr__(self):
        return f"({self.id}, {self.username}, {self.password_hash}, {self.time})"


engine = create_engine("sqlite:///database.db", echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

usernames = session.query(User.username).all()
print(usernames)