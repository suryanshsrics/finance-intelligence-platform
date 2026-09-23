from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi import Depends, HTTPException, status
import jwt
from jwt.exceptions import (InvalidTokenError,
                            ExpiredSignatureError,
                            InvalidSignatureError,
                            InvalidAudienceError,
                            InvalidIssuerError,
                            DecodeError)

from app.auth.keycloak import get_keycloak_public_key
from app.utils.settings import settings

oauth2_scheme = OAuth2AuthorizationCodeBearer(
                authorizationUrl=f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/auth",
                tokenUrl=f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/token"
)
issuer = f"{settings.keycloak_url}/realms/{settings.keycloak_realm}"

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        header = jwt.get_unverified_header(token)
        kid = header["kid"]
        public_key = get_keycloak_public_key(kid)

        payload = jwt.decode(token, public_key, algorithms=["RS256"], issuer=issuer, audience="account")
        return payload

    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token has expired.') from None
    except InvalidAudienceError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token audience.') from None
    except InvalidIssuerError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token issuer.') from None
    except InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token signature.') from None
    except DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token.') from None
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials.") from None
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials.') from None