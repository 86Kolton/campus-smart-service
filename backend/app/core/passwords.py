from __future__ import annotations

import hashlib
import secrets
from secrets import compare_digest


PBKDF2_ALGORITHM = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 390000


def new_salt() -> str:
    return secrets.token_hex(16)


def _pbkdf2_digest(password: str, salt: str, iterations: int) -> str:
    raw = str(password or "").encode("utf-8")
    salt_bytes = str(salt or "").encode("utf-8")
    digest = hashlib.pbkdf2_hmac("sha256", raw, salt_bytes, int(iterations))
    return digest.hex()


def hash_password(password: str, salt: str | None = None, iterations: int = PBKDF2_ITERATIONS) -> str:
    safe_salt = str(salt or new_salt()).strip()
    safe_iterations = max(120000, int(iterations or PBKDF2_ITERATIONS))
    digest = _pbkdf2_digest(password, safe_salt, safe_iterations)
    return f"{PBKDF2_ALGORITHM}${safe_iterations}${safe_salt}${digest}"


def verify_password(raw_password: str, stored_hash: str, stored_salt: str | None = None) -> bool:
    raw = str(raw_password or "")
    stored = str(stored_hash or "").strip()
    if not stored:
        return False

    if stored.startswith(f"{PBKDF2_ALGORITHM}$"):
        parts = stored.split("$", 3)
        if len(parts) != 4:
            return False
        _, iterations_text, salt, digest = parts
        try:
            iterations = int(iterations_text)
        except ValueError:
            return False
        expected = _pbkdf2_digest(raw, salt, iterations)
        return compare_digest(expected, digest)

    if stored.startswith("sha256$") and "$" in stored[7:]:
        parts = stored.split("$")
        if len(parts) == 3:
            salt = parts[1]
            legacy = hashlib.sha256(f"{salt}:{raw}".encode("utf-8")).hexdigest()
            return compare_digest(stored, f"sha256${salt}${legacy}")

    if stored.startswith("sha256$") and "$" not in stored[7:]:
        legacy_digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return compare_digest(stored, f"sha256${legacy_digest}")

    if stored.startswith("sha256$") and stored_salt:
        legacy = hashlib.sha256(f"{stored_salt}:{raw}".encode("utf-8")).hexdigest()
        return compare_digest(stored, f"sha256${stored_salt}${legacy}")

    # Backward compatibility for old demo rows that stored plaintext.
    return compare_digest(raw, stored)


def needs_password_rehash(stored_hash: str, stored_salt: str | None = None) -> bool:
    stored = str(stored_hash or "").strip()
    if not stored.startswith(f"{PBKDF2_ALGORITHM}$"):
        return True

    parts = stored.split("$", 3)
    if len(parts) != 4:
        return True
    try:
        iterations = int(parts[1])
    except ValueError:
        return True
    if iterations < PBKDF2_ITERATIONS:
        return True

    salt = str(parts[2] or "").strip()
    if not salt and stored_salt:
        return True
    return False
