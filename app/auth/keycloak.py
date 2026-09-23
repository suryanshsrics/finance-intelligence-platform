import httpx
from jwt.algorithms import RSAAlgorithm
import json
from app.utils.settings import settings


# JWKS_URL_FORMAT = {KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs

JWKS_CACHE = {}

def get_keycloak_public_key(kid: str):
    keycloak_jwks_url = f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/certs"
    if kid in JWKS_CACHE:
        # kid_json = json.dumps(kid)
        return JWKS_CACHE[kid]
    
    response = httpx.get(keycloak_jwks_url)
    # print('Fetching public key from KEYCLOAK')
    response.raise_for_status()

    data = response.json()
    keys = data["keys"]

    for key in keys:
        kj = json.dumps(key)
        public_key = RSAAlgorithm.from_jwk(kj)
        JWKS_CACHE[key['kid']] = public_key

        if key["kid"] == kid:
            # key_json = json.dumps(key)
            # public_key = RSAAlgorithm.from_jwk(key_json)
            # JWKS_CACHE[kid] = public_key
            return public_key
        
    raise ValueError(f"No Keycloak signing key found for kid: {kid}")



