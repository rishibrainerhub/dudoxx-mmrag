import secrets
import string
from datetime import datetime, timezone
from typing import List
from fastapi import Depends, Request, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from passlib.hash import bcrypt
from fastapi.security import APIKeyHeader


from dudoxx.database.sqlite.database import get_db
from dudoxx.database.sqlite.models import APIKey
from dudoxx.exceptions.apikey_exceptions import (
    APIKeyCreationError,
    APIKeyValidationError,
    APIKeyRevocationError,
    ApiKeyNotFound,
)
from dudoxx.schemas.api_key import ApiKeyResponse


class APIKeyManagerService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    @staticmethod
    async def generate_api_key(length: int = 32) -> str:
        alphabet = string.ascii_letters + string.digits
        return "dud-" + "".join(secrets.choice(alphabet) for _ in range(length))

    async def create_new_api_key(self) -> ApiKeyResponse:
        api_key = await self.generate_api_key()
        try:
            hashed_key = bcrypt.hash(api_key)
            db_key = APIKey(key=api_key[:8], hashed_key=hashed_key)
            self.db.add(db_key)
            self.db.commit()
            return ApiKeyResponse(key=api_key)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise APIKeyCreationError(f"Failed to create API key: {str(e)}")

    async def validate_api_key(self, api_key: str, db: Session) -> bool:
        try:
            db_key = db.query(APIKey).filter(APIKey.key == api_key[:8]).first()
            if db_key and bcrypt.verify(api_key, db_key.hashed_key):
                db_key.last_used = datetime.now(tz=timezone.utc)
                db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.rollback()
            raise APIKeyValidationError(f"Failed to validate API key: {str(e)}") from e

    async def list_api_keys(self) -> List[ApiKeyResponse]:
        try:
            keys = self.db.query(APIKey).all()
            return [ApiKeyResponse(key=key.key) for key in keys]
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to list API keys: {str(e)}") from e

    async def revoke_api_key(self, api_key: str) -> bool:
        try:
            db_key = self.db.query(APIKey).filter(APIKey.key == api_key[:8]).first()
            if not db_key:
                raise ApiKeyNotFound()
            self.db.delete(db_key)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise APIKeyRevocationError(f"Failed to revoke API key: {str(e)}") from e


class ApiKeyMiddleware(APIKeyHeader):
    def __init__(self):
        super().__init__(name="X-API-Key", auto_error=False)
        self.api_key_manager = APIKeyManagerService()
        self.db = next(get_db())

    async def __call__(self, request: Request):
        api_key = await super().__call__(request)
        if api_key is None:
            raise HTTPException(status_code=401, detail="API Key is missing")
        try:
            if await self.api_key_manager.validate_api_key(api_key, self.db):
                return api_key
            else:
                raise HTTPException(status_code=403, detail="Invalid API Key")
        except APIKeyValidationError as e:
            raise HTTPException(status_code=500, detail=f"API key validation error: {str(e)}")
