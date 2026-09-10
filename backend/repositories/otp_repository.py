from datetime import datetime, timezone, timedelta
from typing import Optional
from core.database import get_db
from core.exceptions import DatabaseOperationError
from services.cache_service import CacheService
from core.logging import get_logger

logger = get_logger(__name__)


class OTPRepository:
    def __init__(self, cache_service: Optional[CacheService] = None):
        self.cache = cache_service or CacheService()

    @property
    def collection(self):
        db = get_db()
        return db["otp_verifications"]

    async def ensure_ttl_index(self):
        try:
            await self.collection.create_index("expires_at", expireAfterSeconds=0)
            await self.collection.create_index("email", unique=True)
        except Exception:
            pass

    async def is_cooldown_active(self, email: str) -> bool:
        if self.cache.is_enabled:
            key = f"otp:cooldown:{email.lower()}"
            val = await self.cache.get_json(key)
            return val is not None
        return False

    async def set_cooldown(self, email: str, ttl_seconds: int = 30) -> None:
        if self.cache.is_enabled:
            key = f"otp:cooldown:{email.lower()}"
            await self.cache.set_json(key, "active", ttl_seconds=ttl_seconds)

    async def save_otp(
        self,
        email: str,
        name: str,
        password_hash: str,
        otp_hash: str,
        ttl_minutes: int = 5,
    ) -> None:
        email_clean = email.lower().strip()
        ttl_seconds = ttl_minutes * 60

        # Try Upstash Redis first
        if self.cache.is_enabled:
            record = {
                "email": email_clean,
                "name": name,
                "password_hash": password_hash,
                "otp_hash": otp_hash,
                "attempts": 0,
            }
            key = f"otp:hash:{email_clean}"
            await self.cache.set_json(key, record, ttl_seconds=ttl_seconds)
            await self.set_cooldown(email_clean, ttl_seconds=30)
            logger.info(f"[OTPRepository] Saved OTP to Redis | email={email_clean}")

        # Always persist backup in MongoDB for reliability
        try:
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(minutes=ttl_minutes)
            doc = {
                "email": email_clean,
                "name": name,
                "password_hash": password_hash,
                "otp_hash": otp_hash,
                "attempts": 0,
                "created_at": now,
                "expires_at": expires_at,
            }
            await self.collection.update_one(
                {"email": email_clean},
                {"$set": doc},
                upsert=True,
            )
        except Exception as e:
            if not self.cache.is_enabled:
                raise DatabaseOperationError(f"Failed to save OTP verification record: {e}")

    async def get_otp_by_email(self, email: str) -> dict | None:
        email_clean = email.lower().strip()

        if self.cache.is_enabled:
            key = f"otp:hash:{email_clean}"
            cached_doc = await self.cache.get_json(key)
            if cached_doc:
                return cached_doc

        try:
            return await self.collection.find_one({"email": email_clean})
        except Exception as e:
            raise DatabaseOperationError(f"Failed to fetch OTP record: {e}")

    async def increment_attempts(self, email: str) -> int:
        email_clean = email.lower().strip()

        if self.cache.is_enabled:
            key = f"otp:hash:{email_clean}"
            cached_doc = await self.cache.get_json(key)
            if cached_doc:
                attempts = cached_doc.get("attempts", 0) + 1
                cached_doc["attempts"] = attempts
                await self.cache.set_json(key, cached_doc, ttl_seconds=300)
                return attempts

        try:
            result = await self.collection.find_one_and_update(
                {"email": email_clean},
                {"$inc": {"attempts": 1}},
                return_document=True,
            )
            return result.get("attempts", 1) if result else 1
        except Exception as e:
            raise DatabaseOperationError(f"Failed to update OTP attempt count: {e}")

    async def delete_otp(self, email: str) -> None:
        email_clean = email.lower().strip()

        if self.cache.is_enabled:
            key = f"otp:hash:{email_clean}"
            cooldown_key = f"otp:cooldown:{email_clean}"
            await self.cache.delete(key)
            await self.cache.delete(cooldown_key)

        try:
            await self.collection.delete_one({"email": email_clean})
        except Exception as e:
            raise DatabaseOperationError(f"Failed to delete OTP verification record: {e}")
