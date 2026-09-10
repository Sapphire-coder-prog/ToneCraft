import os
import jwt
from jwt import PyJWKClient
from fastapi import Request, HTTPException

CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL")
_jwks_client = PyJWKClient(CLERK_JWKS_URL) if CLERK_JWKS_URL else None


def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header")

    token = auth_header.split(" ")[1]

    if not _jwks_client:
        raise HTTPException(500, "CLERK_JWKS_URL not set in .env")

    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
    except Exception as e:
        raise HTTPException(401, f"Invalid token: {e}")

    return payload  # payload["sub"] is the Clerk user id