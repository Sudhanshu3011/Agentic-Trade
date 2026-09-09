from datetime import datetime, timezone, timedelta
from core.database import get_db
from core.exceptions import DatabaseOperationError


class OTPRepository:
    def __init__(self):
        pass

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

    async def save_otp(
        self,
        email: str,
        name: str,
        password_hash: str,
        otp_hash: str,
        ttl_minutes: int = 5,
    ) -> None:
        try:
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(minutes=ttl_minutes)
            doc = {
                "email": email.lower(),
                "name": name,
                "password_hash": password_hash,
                "otp_hash": otp_hash,
                "attempts": 0,
                "created_at": now,
                "expires_at": expires_at,
            }
            await self.collection.update_one(
                {"email": email.lower()},
                {"$set": doc},
                upsert=True,
            )
        except Exception as e:
            raise DatabaseOperationError(f"Failed to save OTP verification record: {e}")

    async def get_otp_by_email(self, email: str) -> dict | None:
        try:
            return await self.collection.find_one({"email": email.lower()})
        except Exception as e:
            raise DatabaseOperationError(f"Failed to fetch OTP record: {e}")

    async def increment_attempts(self, email: str) -> int:
        try:
            result = await self.collection.find_one_and_update(
                {"email": email.lower()},
                {"$inc": {"attempts": 1}},
                return_document=True,
            )
            return result.get("attempts", 1) if result else 1
        except Exception as e:
            raise DatabaseOperationError(f"Failed to update OTP attempt count: {e}")

    async def delete_otp(self, email: str) -> None:
        try:
            await self.collection.delete_one({"email": email.lower()})
        except Exception as e:
            raise DatabaseOperationError(f"Failed to delete OTP verification record: {e}")
