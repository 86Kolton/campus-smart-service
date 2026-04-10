from __future__ import annotations

import re
import sys
from pathlib import Path

from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import SessionLocal
from app.models.errand_task import ErrandTask
from app.models.post import Post
from app.models.user import User
from app.services.bootstrap_service import bootstrap_database
from app.services.post_service import post_service


VALIDATION_PATTERN = re.compile(r"(验证贴\s*[ab]?|图文验证贴|验证跑腿|domain-current|local-current|smoke_[ab]_)", re.IGNORECASE)


def should_cleanup_post(post: Post, author_username: str) -> bool:
    haystack = " ".join([
        str(post.title or ""),
        str(post.content or ""),
        str(author_username or ""),
    ])
    return bool(VALIDATION_PATTERN.search(haystack))


def should_cleanup_errand(task: ErrandTask, author_username: str) -> bool:
    haystack = " ".join([
        str(task.title or ""),
        str(task.note or ""),
        str(author_username or ""),
    ])
    return bool(VALIDATION_PATTERN.search(haystack))


def main() -> None:
    bootstrap_database()
    removed_posts = 0
    removed_errands = 0

    with SessionLocal() as db:
        post_rows = db.execute(
            select(Post.id, Post.author_id, Post.title, Post.content, User.username).join(User, User.id == Post.author_id)
        ).all()

    for post_id, author_id, title, content, username in post_rows:
        post = Post(id=int(post_id), author_id=int(author_id), title=str(title or ""), content=str(content or ""))
        if not should_cleanup_post(post, str(username or "")):
            continue
        try:
            post_service.delete_post(f"p-{int(post_id)}", int(author_id))
            removed_posts += 1
        except Exception as exc:  # pragma: no cover - maintenance script
            print(f"skip post p-{int(post_id)}: {exc}")

    with SessionLocal() as db:
        errand_rows = db.execute(
            select(ErrandTask.id, ErrandTask.title, ErrandTask.note, User.username, ErrandTask)
            .join(User, User.id == ErrandTask.publisher_id)
        ).all()
        for task_id, title, note, username, task in errand_rows:
            task.title = str(title or "")
            task.note = str(note or "")
            if not should_cleanup_errand(task, str(username or "")):
                continue
            db.delete(task)
            removed_errands += 1
        db.commit()

    print(f"removed_posts={removed_posts}")
    print(f"removed_errands={removed_errands}")


if __name__ == "__main__":
    main()
