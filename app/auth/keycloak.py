import httpx
from jwt.algorithms import RSAAlgorithm
import json
from app.utils.settings import settings


# JWKS_URL_FORMAT = {KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs

def get_keycloak_public_key(kid: str):
    keycloak_jwks_url = f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/certs"

    response = httpx.get(keycloak_jwks_url)
    response.raise_for_status()

    data = response.json()
    keys = data["keys"]

    for key in keys:
        if key["kid"] == kid:
            key_json = json.dumps(key)
            public_key = RSAAlgorithm.from_jwk(key_json)
            return public_key
        
    raise ValueError(f"No Keycloak signing key found for kid: {kid}")



