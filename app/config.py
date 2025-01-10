import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+mysqlconnector://Pablo:1590@localhost:3306/messenger_db"
)
