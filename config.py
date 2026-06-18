import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL_QUOTE = "https://dev2-mt-quote-management.paas.telekom.hu"
BASE_URL_AGREEMENT = "https://dev2-mt-agreement.paas.telekom.hu"

HEADERS_QUOTE = {
    "x-request-session-id": "a",
    "x-request-tracking-id": "a",
    "x-request-id": "a",
    "x-channel-id": "IFE",
    "brand": "MT",
    "x-m2m-user-id": "",
    "x-http-method-override": "POST",
    "x-api-key": os.getenv("QUOTE_API_KEY"),
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
    "x-api-key": os.getenv("AGREEMENT_API_KEY"),
}
