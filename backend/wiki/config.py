import os
from dotenv import load_dotenv

load_dotenv()

WIKIPEDIA_API_URL = os.getenv("WIKIPEDIA_API_URL", "https://en.wikipedia.org/w/api.php")
