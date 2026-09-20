from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
import jwt

from app.auth.keycloak import get_keycloak_public_key
from app.utils.settings import settings

oauth2_scheme = HTTPBearer()
issuer = f"{settings.keycloak_url}/realms/{settings.keycloak_realm}"

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = credentials.credentials
    header = jwt.get_unverified_header(token)
    kid = header["kid"]
    public_key = get_keycloak_public_key(kid)

    payload = jwt.decode(token, public_key, algorithms=["RS256"], issuer=issuer, audience="account")
    return payload