import os

from dotenv import load_dotenv

load_dotenv()

host = os.getenv("PG_HOST")
port = os.getenv("PG_POR")
PG_USER = os.getenv("PG_USER")
PG_PASS = os.getenv("PG_PASS")
DB_NAME = os.getenv("DB_NAME")

# Ссылка подключения к базе данных
POSTGRES_URI = f"postgresql://{PG_USER}:{PG_PASS}@{host}/{DB_NAME}"

ip = os.getenv("ip")
