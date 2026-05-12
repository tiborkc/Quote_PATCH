import os
from dotenv import load_dotenv

load_dotenv(override=True)

ENV = os.getenv(
    "ENVIRONMENT", "dev2"
)  # env fájlban válassz környezetet. ez a default érték, ha nincs megadva.

if ENV == "dev1":
    BASE_URL_AGREEMENT = os.getenv("DEV1_AGREEMENT_URL")
    BASE_URL_QUOTE = os.getenv("DEV1_QUOTE_URL")

    COMMON_API_KEY = os.getenv("DEV1_COMMON_API_KEY")
    POST_API_KEY = os.getenv("DEV1_POST_API_KEY")

elif ENV == "dev2":
    BASE_URL_AGREEMENT = os.getenv("DEV2_AGREEMENT_URL")
    BASE_URL_QUOTE = os.getenv("DEV2_QUOTE_URL")

    COMMON_API_KEY = os.getenv("DEV2_COMMON_API_KEY")
    POST_API_KEY = os.getenv("DEV2_POST_API_KEY")

else:
    raise ValueError(f"Unknown environment: {ENV}")

QUOTE_ID = os.getenv("QUOTE_ID")
MTID = os.getenv("MTID")
MONOGRAM = os.getenv("MONOGRAM")
