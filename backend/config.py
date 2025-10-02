import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://root:mypassword@127.0.0.1:5432/nsightTechnicalTest")
UPSTREAM_API_URL = os.getenv("UPSTREAM_API_URL", "https://jsonplaceholder.typicode.com/users/1")
CACHE_DURATION_MINUTES = int(os.getenv("CACHE_DURATION_MINUTES", "10"))

