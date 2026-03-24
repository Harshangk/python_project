# python db_test.py

########### To check DB Connection

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Database connected successfully")
except Exception as e:
    print("Database connection failed")
    print(e)



########### To check password Hash

# from passlib.context import CryptContext

# pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# hash = pwd.hash("string")

# print(hash)
# # print(pwd.verify("string", hash))