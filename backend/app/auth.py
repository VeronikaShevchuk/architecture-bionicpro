from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from jose import jwk
import httpx
from app.config import settings
import logging
from functools import lru_cache
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
security = HTTPBearer()

# Кеш для публичных ключей
_cached_keys = {}
_cache_time = 0
_CACHE_TTL = 3600  # 1 час

async def get_keycloak_public_keys():
    """Получение публичных ключей Keycloak с кешированием."""
    global _cached_keys, _cache_time
    
    # Если кеш свежий — возвращаем его
    if _cached_keys and (time.time() - _cache_time) < _CACHE_TTL:
        return _cached_keys
    
    realm_url = f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}"
    certs_url = f"{realm_url}/protocol/openid-connect/certs"
    
    logger.info(f"Fetching public keys from: {certs_url}")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(certs_url)
        response.raise_for_status()
        jwks = response.json()
        
        # Сохраняем в кеш
        _cached_keys = jwks["keys"]
        _cache_time = time.time()
        
        logger.info(f"✅ Loaded {len(_cached_keys)} public keys")
        return _cached_keys

def pem_to_public_key(pem_str: str):
    """Конвертирует PEM строку в формат, понятный python-jose."""
    return pem_str

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Валидация JWT токена с автоматическим получением ключа."""
    token = credentials.credentials
    
    try:
        # Получаем заголовок токена
        header = jwt.get_unverified_header(token)
        token_kid = header.get('kid')
        logger.info(f"Token kid: {token_kid}")
        
        # Получаем все публичные ключи из Keycloak
        keys = await get_keycloak_public_keys()
        
        # Ищем ключ с matching kid
        matching_key = None
        for key in keys:
            if key.get('kid') == token_kid:
                matching_key = key
                logger.info(f"Found matching key: {key.get('kid')} (alg: {key.get('alg')})")
                break
        
        if not matching_key:
            logger.error(f"No matching key found for kid: {token_kid}")
            raise HTTPException(status_code=401, detail="No matching public key")
        
        # Конвертируем JWK в PEM
        public_key = jwk.construct(matching_key, algorithm="RS256").to_pem().decode('utf-8')
        
        # Декодируем без проверки для получения issuer/audience
        unverified = jwt.get_unverified_claims(token)
        logger.info(f"Token issuer: {unverified.get('iss')}, sub: {unverified.get('sub')}")
        
        # Проверяем токен
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=unverified.get('aud'),
            issuer=unverified.get('iss'),
            options={"verify_exp": True}
        )
        
        logger.info(f"✅ Token verified for user: {payload.get('preferred_username')}")
        return payload
        
    except JWTError as e:
        logger.error(f"❌ JWT verification failed: {e}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

def get_current_user(payload: dict = Depends(verify_token)):
    """Извлечение информации о пользователе из токена."""
    return {
        "sub": payload.get("sub"),
        "preferred_username": payload.get("preferred_username"),
        "email": payload.get("email")
    }