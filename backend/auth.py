import os
import jwt
from jwt import PyJWKClient
from fastapi import Request, HTTPException


def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header")

    token = auth_header.split(" ")[1]

    # Read the environment variable when the request arrives
    clerk_jwks_url = os.getenv("CLERK_JWKS_URL")

    if not clerk_jwks_url:
        raise HTTPException(500, "CLERK_JWKS_URL not set")

    try:
        jwks_client = PyJWKClient(clerk_jwks_url)

        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )

    except Exception as e:
        raise HTTPException(401, f"Invalid token: {e}")

    return payload