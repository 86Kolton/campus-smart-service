from __future__ import annotations

import secrets

from sqlalchemy import func, select

from app.core.passwords import hash_password, needs_password_rehash, new_salt, verify_password
from app.core.database import SessionLocal
from app.models.user import User


def _hash_password(password: str, salt: str) -> str:
    return hash_password(password, salt=salt)


def _new_salt() -> str:
    return new_salt()


def _verify_password(raw_password: str, stored_hash: str, stored_salt: str | None = None) -> bool:
    return verify_password(raw_password, stored_hash, stored_salt)


class UserService:
    @staticmethod
    def is_placeholder_display_name(display_name: str | None) -> bool:
        text = str(display_name or "").strip().replace("@", "")
        if not text:
            return True
        return text in {"校园访客", "微信访客", "微信用户", "访客", "游客"}

    @staticmethod
    def build_default_public_name(display_name: str | None) -> str:
        safe_display = str(display_name or "").strip().replace("@", "")
        if not safe_display:
            return "校园同学"
        if safe_display.endswith("同学"):
            return safe_display[:24]
        org_markers = ("组", "队", "馆", "堂", "中心", "实验室", "助手")
        if any(marker in safe_display for marker in org_markers):
            return safe_display[:24]
        return f"{safe_display[0]}同学"

    @staticmethod
    def normalize_public_name(value: str | None, fallback_display_name: str | None = None) -> str:
        text = str(value or "").strip().replace("@", "")
        if not text or UserService.is_placeholder_display_name(text):
            return UserService.build_default_public_name(fallback_display_name)
        return text[:24]

    def get_public_name(self, user: User | None) -> str:
        if not user:
            return "匿名用户"
        nickname = str(getattr(user, "nickname", None) or "").strip()
        display_name = str(getattr(user, "display_name", None) or "").strip()
        if self.is_placeholder_display_name(nickname):
            nickname = ""
        return self.normalize_public_name(nickname, display_name)

    def get_visible_profile_name(self, user: User | None) -> str:
        if not user:
            return "校园同学"
        display_name = str(getattr(user, "display_name", None) or "").strip()
        public_name = self.get_public_name(user)
        if self.is_placeholder_display_name(display_name):
            return public_name
        return display_name or public_name

    def authenticate_client(self, username: str, password: str) -> User | None:
        safe_username = str(username or "").strip()
        safe_password = str(password or "")
        if not safe_username or not safe_password:
            return None

        with SessionLocal() as db:
            user = db.execute(select(User).where(User.username == safe_username)).scalar_one_or_none()
            if not user:
                return None
            if user.role != "client" or user.status != "active":
                return None
            if not _verify_password(safe_password, user.password_hash, user.password_salt):
                return None

            if needs_password_rehash(user.password_hash, user.password_salt):
                salt = _new_salt()
                user.password_salt = salt
                user.password_hash = _hash_password(safe_password, salt)
                db.add(user)
                db.commit()
                db.refresh(user)
            return user

    def register_client(self, username: str, display_name: str, password: str) -> User:
        safe_username = str(username or "").strip()
        safe_display_name = str(display_name or "").strip()
        safe_password = str(password or "")

        if len(safe_username) < 3:
            raise ValueError("username_too_short")
        if len(safe_password) < 6:
            raise ValueError("password_too_short")
        if not safe_display_name:
            raise ValueError("display_name_required")

        with SessionLocal() as db:
            exists = db.execute(select(User.id).where(User.username == safe_username)).scalar_one_or_none()
            if exists:
                raise ValueError("username_already_exists")

            next_id = int(db.scalar(select(func.max(User.id))) or 0) + 1
            salt = _new_salt()
            user = User(
                id=next_id,
                username=safe_username,
                display_name=safe_display_name[:128],
                nickname=self.build_default_public_name(safe_display_name),
                password_hash=_hash_password(safe_password, salt),
                password_salt=salt,
                role="client",
                status="active",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user

    def get_user(self, user_id: int) -> User | None:
        with SessionLocal() as db:
            return db.get(User, int(user_id))

    def get_first_active_client(self) -> User | None:
        with SessionLocal() as db:
            return (
                db.execute(
                    select(User)
                    .where(User.role == "client", User.status == "active")
                    .order_by(User.id.asc())
                    .limit(1)
                ).scalar_one_or_none()
            )

    def update_public_name(self, user_id: int, public_name: str) -> User:
        with SessionLocal() as db:
            user = db.get(User, int(user_id))
            if not user:
                raise ValueError("client_not_found")
            user.nickname = self.normalize_public_name(public_name, user.display_name)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user

    def bind_openid(self, user_id: int, openid: str) -> None:
        safe_openid = str(openid or "").strip()
        if not safe_openid:
            raise ValueError("wechat_openid_required")
        with SessionLocal() as db:
            existing = db.execute(select(User).where(User.wechat_openid == safe_openid)).scalar_one_or_none()
            if existing and int(existing.id) != int(user_id):
                raise ValueError("wechat_openid_in_use")
            user = db.get(User, int(user_id))
            if not user:
                raise ValueError("client_not_found")
            user.wechat_openid = safe_openid
            user.nickname = self.normalize_public_name(getattr(user, "nickname", None), user.display_name)
            if self.is_placeholder_display_name(user.display_name):
                user.display_name = self.get_public_name(user)
            db.add(user)
            db.commit()

    def get_or_create_by_openid(self, openid: str, display_name: str | None = None) -> User:
        safe_openid = str(openid or "").strip()
        if not safe_openid:
            raise ValueError("wechat_openid_required")
        safe_display = str(display_name or "").strip() or "微信用户"
        with SessionLocal() as db:
            existing = db.execute(select(User).where(User.wechat_openid == safe_openid)).scalar_one_or_none()
            if existing:
                changed = False
                normalized_public_name = self.normalize_public_name(getattr(existing, "nickname", None), existing.display_name)
                if str(getattr(existing, "nickname", None) or "").strip() != normalized_public_name:
                    existing.nickname = normalized_public_name
                    changed = True
                if self.is_placeholder_display_name(existing.display_name):
                    existing.display_name = normalized_public_name
                    changed = True
                if changed:
                    db.add(existing)
                    db.commit()
                    db.refresh(existing)
                return existing

            base_username = f"wx_{safe_openid[-10:]}"
            username = base_username
            suffix = 1
            while db.execute(select(User.id).where(User.username == username)).scalar_one_or_none():
                suffix += 1
                username = f"{base_username}_{suffix}"

            next_id = int(db.scalar(select(func.max(User.id))) or 0) + 1
            salt = _new_salt()
            user = User(
                id=next_id,
                username=username,
                display_name=safe_display[:128],
                nickname=self.build_default_public_name(safe_display),
                password_hash=_hash_password(secrets.token_hex(8), salt),
                password_salt=salt,
                role="client",
                status="active",
                wechat_openid=safe_openid,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user


user_service = UserService()
