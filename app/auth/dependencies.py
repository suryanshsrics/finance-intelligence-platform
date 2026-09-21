from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi import Depends
import jwt

from app.auth.keycloak import get_keycloak_public_key
from app.utils.settings import settings

oauth2_scheme = OAuth2AuthorizationCodeBearer(
                authorizationUrl=f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/auth",
                tokenUrl=f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/token"
)
issuer = f"{settings.keycloak_url}/realms/{settings.keycloak_realm}"

def get_current_user(token: str = Depends(oauth2_scheme)):
    header = jwt.get_unverified_header(token)
    kid = header["kid"]
    public_key = get_keycloak_public_key(kid)

    payload = jwt.decode(token, public_key, algorithms=["RS256"], issuer=issuer, audience="account")
    return payload