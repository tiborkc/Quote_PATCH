import os
from dotenv import load_dotenv

load_dotenv(override=True)


CURRENT_ENV = os.getenv("ENVIRONMENT", "dev1")

#AGREEMENT URL beállítás
AGREEMENT_URLS = {
    "dev1": os.getenv("DEV1_AGREEMENT_URL"),
    "dev2": os.getenv("DEV2_AGREEMENT_URL"),
}

BASE_URL_AGREEMENT = AGREEMENT_URLS.get(CURRENT_ENV)
if not BASE_URL_AGREEMENT:
    raise ValueError(f"Nincs BASE_URL_AGREEMENT beállítva ehhez: {CURRENT_ENV}")

#AGREEMENT API KEY beállítás
AGREEMENT_API_KEYS = {
    "dev1": os.getenv("DEV1_POST_API_KEY"),
    "dev2": os.getenv("DEV2_POST_API_KEY"),
}

AGREEMENT_API_KEY = AGREEMENT_API_KEYS.get(CURRENT_ENV)
if not AGREEMENT_API_KEY:
    raise ValueError(f"Nincs AGREEMENT_API_KEY beállítva ehhez: {CURRENT_ENV}")


#QUOTE URL beállítás
QUOTE_URLS = {
    "dev1": os.getenv("DEV1_QUOTE_URL"),
    "dev2": os.getenv("DEV2_QUOTE_URL"),
}

BASE_URL_QUOTE = QUOTE_URLS.get(CURRENT_ENV)
if not BASE_URL_QUOTE:
    raise ValueError(f"Nincs BASE_URL_QUOTE beállítva ehhez: {CURRENT_ENV}")

#QUOTE API KEY beállítás
QUOTE_API_KEYS = {
    "dev1": os.getenv("DEV1_COMMON_API_KEY"),
    "dev2": os.getenv("DEV2_COMMON_API_KEY"),
}

QUOTE_API_KEY = QUOTE_API_KEYS.get(CURRENT_ENV)
if not QUOTE_API_KEY:
    raise ValueError(f"Nincs QUOTE_API_KEY beállítva ehhez: {CURRENT_ENV}")


HEADERS_QUOTE = {
    "x-request-session-id": "a",
    "x-request-tracking-id": "a",
    "x-request-id": "a",
    "x-channel-id": "IFE",
    "brand": "MT",
    "x-m2m-user-id": "",
    "x-http-method-override": "POST",
    "x-api-key": QUOTE_API_KEY,
    "Content-Type": "application/json",
    "accept": "application/json",
}

HEADERS_AGREEMENT = {
    "accept": "application/json",
    "x-request-tracking-id": "requestTracingId123",
    "x-request-session-id": "requestSessionId123",
    "x-request-id": "requestId123",
    "X-Client-Version": "clientVersion123",
    "X-Client-Id": "clientId123",
    "x-channel-id": "B2B",
    "brand": "MT",
    "x-m2m-user-id": "m2mUserId123",
    "Content-Type": "application/json",
    "x-api-key": AGREEMENT_API_KEY,
}

MONOGRAM = os.getenv("MONOGRAM", "UNKNOWN")