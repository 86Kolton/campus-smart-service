from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models.errand_task import ErrandTask
from app.models.user import User
from app.services.user_service import user_service


TASK_TYPE_LABELS = {
    "quick": "快速代取",
    "delivery": "外卖代拿",
    "print": "打印跑腿",
    "other": "其他跑腿",
}

STATUS_LABELS = {
    "open": "待接单",
    "inprogress": "进行中",
    "waiting_confirm": "待确认",
    "done": "已完成",
    "canceled": "已撤销",
}

STATUS_TONES = {
    "open": "blue",
    "inprogress": "mint",
    "waiting_confirm": "sand",
    "done": "teal",
    "canceled": "gray",
}

STATUS_ORDER = {"open": 0, "inprogress": 1, "waiting_confirm": 2, "done": 3, "canceled": 4}


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def _parse_task_id(task_id: str) -> int:
    return int(str(task_id).replace("e-", ""))


def _normalize_status(status: str) -> str:
    safe = str(status or "").strip()
    return safe if safe in STATUS_LABELS else "open"


def _format_relative(dt: datetime | None) -> str:
    if not dt:
        return "刚刚"
    current = _utcnow()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    seconds = int((current - dt).total_seconds())
    if seconds < 60:
        return "刚刚"
    if seconds < 3600:
        return f"{max(1, seconds // 60)} 分钟前"
    if seconds < 86400:
        return f"{max(1, seconds // 3600)} 小时前"
    return f"{max(1, seconds // 86400)} 天前"


def _format_clock(dt: datetime | None) -> str:
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone().strftime("%m-%d %H:%M")


def _normalize_reward(raw: str) -> str:
    text = str(raw or "").strip() or "5"
    return text if text.startswith("￥") else f"￥{text}"


def _primary_action(task: ErrandTask, viewer_user_id: int) -> dict:
    is_publisher = int(task.publisher_id) == int(viewer_user_id)
    is_runner = bool(task.runner_id) and int(task.runner_id or 0) == int(viewer_user_id)
    status = _normalize_status(task.status)
    if status == "open":
        if is_publisher:
            return {"key": "cancel", "label": "撤销任务", "tone": "ghost"}
        return {"key": "claim", "label": "我要接单", "tone": "primary"}
    if status == "inprogress":
        if is_runner:
            return {"key": "delivered", "label": "我已送达", "tone": "primary"}
        return {"key": "detail", "label": "查看进度", "tone": "ghost"}
    if status == "waiting_confirm":
        if is_publisher:
            return {"key": "confirm", "label": "确认完成", "tone": "primary"}
        return {"key": "detail", "label": "等待确认", "tone": "ghost"}
    if status in {"done", "canceled"} and is_publisher:
        return {"key": "delete", "label": "删除任务", "tone": "ghost"}
    return {"key": "detail", "label": "查看详情", "tone": "ghost"}


def _timeline(task: ErrandTask) -> list[dict]:
    return [
        {"key": "created", "label": "发布", "value": _format_clock(task.created_at) or "刚刚"},
        {"key": "accepted", "label": "接单", "value": _format_clock(task.accepted_at)} if task.accepted_at else None,
        {"key": "delivered", "label": "送达", "value": _format_clock(task.delivered_at)} if task.delivered_at else None,
        {"key": "confirmed", "label": "确认", "value": _format_clock(task.confirmed_at)} if task.confirmed_at else None,
    ]


class ErrandService:
    def _to_item(self, task: ErrandTask, viewer_user_id: int, publisher: User | None = None, runner: User | None = None) -> dict:
        status = _normalize_status(task.status)
        is_publisher = int(task.publisher_id) == int(viewer_user_id)
        is_runner = bool(task.runner_id) and int(task.runner_id or 0) == int(viewer_user_id)
        can_view_contact = is_publisher or is_runner
        publisher_name = user_service.get_public_name(publisher)
        runner_name = user_service.get_public_name(runner) if runner else ""
        pickup_location = str(task.pickup_location or "").strip()
        destination = str(task.destination or "").strip()
        location_summary = " · ".join([item for item in [pickup_location, destination] if item])
        return {
            "id": f"e-{int(task.id)}",
            "task_type": str(task.task_type),
            "tag": TASK_TYPE_LABELS.get(str(task.task_type), "跑腿任务"),
            "title": task.title,
            "reward": task.reward,
            "time": task.eta,
            "pickup_location": pickup_location,
            "destination": destination,
            "location_summary": location_summary,
            "note": str(task.note or ""),
            "publisher_id": int(task.publisher_id),
            "publisher_name": publisher_name,
            "publisher_contact": str(task.contact or "") if can_view_contact else "接单后可见",
            "runner_id": int(task.runner_id) if task.runner_id else None,
            "runner_name": runner_name,
            "runner_contact": "站内已接单" if runner_name else "",
            "status": status,
            "status_label": STATUS_LABELS.get(status, "待接单"),
            "status_tone": STATUS_TONES.get(status, "blue"),
            "relative_text": _format_relative(task.created_at),
            "created_at": task.created_at.isoformat() if task.created_at else "",
            "accepted_at": task.accepted_at.isoformat() if task.accepted_at else "",
            "delivered_at": task.delivered_at.isoformat() if task.delivered_at else "",
            "confirmed_at": task.confirmed_at.isoformat() if task.confirmed_at else "",
            "primary_action": _primary_action(task, viewer_user_id),
            "timeline": [item for item in _timeline(task) if item],
            "can_delete": bool(is_publisher and status in {"open", "canceled", "done"}),
            "source_type": "errand",
        }

    def list_tasks(self, viewer_user_id: int) -> list[dict]:
        with SessionLocal() as db:
            rows = db.execute(
                select(ErrandTask, User)
                .join(User, User.id == ErrandTask.publisher_id)
                .order_by(ErrandTask.id.desc())
            ).all()
            runner_ids = [int(row[0].runner_id) for row in rows if row[0].runner_id]
            runner_map = {}
            if runner_ids:
                for user in db.execute(select(User).where(User.id.in_(runner_ids))).scalars().all():
                    runner_map[int(user.id)] = user

        items = [
            self._to_item(
                task=row[0],
                viewer_user_id=viewer_user_id,
                publisher=row[1],
                runner=runner_map.get(int(row[0].runner_id or 0)),
            )
            for row in rows
        ]
        return sorted(
            items,
            key=lambda item: (
                STATUS_ORDER.get(str(item["status"]), 99),
                -int(str(item["id"]).replace("e-", "") or 0),
            ),
        )

    def list_my_tasks(self, viewer_user_id: int) -> list[dict]:
        with SessionLocal() as db:
            rows = db.execute(
                select(ErrandTask, User)
                .join(User, User.id == ErrandTask.publisher_id)
                .where(ErrandTask.publisher_id == int(viewer_user_id))
                .order_by(ErrandTask.id.desc())
            ).all()
            runner_ids = [int(row[0].runner_id) for row in rows if row[0].runner_id]
            runner_map = {}
            if runner_ids:
                for user in db.execute(select(User).where(User.id.in_(runner_ids))).scalars().all():
                    runner_map[int(user.id)] = user
        return [
            self._to_item(
                task=row[0],
                viewer_user_id=viewer_user_id,
                publisher=row[1],
                runner=runner_map.get(int(row[0].runner_id or 0)),
            )
            for row in rows
        ]

    def create_task(
        self,
        publisher_id: int,
        task_type: str,
        title: str,
        reward: str,
        time_text: str,
        pickup_location: str,
        destination: str,
        note: str,
        contact: str,
    ) -> dict:
        safe_title = str(title or "").strip()[:120]
        safe_pickup = str(pickup_location or "").strip()[:128]
        safe_destination = str(destination or "").strip()[:128]
        safe_contact = str(contact or "").strip()[:128]
        if not safe_title:
            raise ValueError("errand_title_required")
        if not safe_pickup:
            raise ValueError("errand_pickup_required")
        if not safe_destination:
            raise ValueError("errand_destination_required")
        if not safe_contact:
            raise ValueError("errand_contact_required")

        with SessionLocal() as db:
            next_id = int(db.scalar(select(func.max(ErrandTask.id))) or 0) + 1
            row = ErrandTask(
                id=next_id,
                publisher_id=int(publisher_id),
                runner_id=None,
                task_type=str(task_type or "quick").strip() or "quick",
                title=safe_title,
                reward=_normalize_reward(reward),
                eta=str(time_text or "").strip()[:64] or "尽快",
                pickup_location=safe_pickup,
                destination=safe_destination,
                note=str(note or "").strip()[:500],
                contact=safe_contact,
                status="open",
                created_at=_utcnow(),
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            publisher = db.get(User, int(publisher_id))
        return self._to_item(task=row, viewer_user_id=publisher_id, publisher=publisher, runner=None)

    def apply_action(self, task_id: str, action: str, user_id: int) -> dict:
        try:
            raw_id = _parse_task_id(task_id)
        except ValueError as exc:
            raise ValueError("errand_not_found") from exc

        with SessionLocal() as db:
            task = db.get(ErrandTask, raw_id)
            if not task:
                raise ValueError("errand_not_found")
            now = _utcnow()
            status = _normalize_status(task.status)
            is_publisher = int(task.publisher_id) == int(user_id)
            is_runner = bool(task.runner_id) and int(task.runner_id or 0) == int(user_id)

            if action == "delete":
                if status not in {"open", "done", "canceled"}:
                    raise ValueError("errand_status_conflict")
                if not is_publisher:
                    raise ValueError("errand_delete_forbidden")
                publisher = db.get(User, int(task.publisher_id))
                runner = db.get(User, int(task.runner_id)) if task.runner_id else None
                snapshot = self._to_item(task=task, viewer_user_id=user_id, publisher=publisher, runner=runner)
                snapshot["can_delete"] = False
                snapshot["primary_action"] = {"key": "detail", "label": "已删除", "tone": "ghost"}
                db.delete(task)
                db.commit()
                return {
                    "item": snapshot,
                    "message": "任务已删除",
                }
            if action == "claim":
                if status != "open":
                    raise ValueError("errand_status_conflict")
                if is_publisher:
                    raise ValueError("errand_claim_self_forbidden")
                task.status = "inprogress"
                task.runner_id = int(user_id)
                task.accepted_at = now
                message = "接单成功，请按约定联系发布者"
            elif action == "delivered":
                if status != "inprogress":
                    raise ValueError("errand_status_conflict")
                if not is_runner:
                    raise ValueError("errand_deliver_forbidden")
                task.status = "waiting_confirm"
                task.delivered_at = now
                message = "已标记送达，等待发布方确认"
            elif action == "confirm":
                if status != "waiting_confirm":
                    raise ValueError("errand_status_conflict")
                if not is_publisher:
                    raise ValueError("errand_confirm_forbidden")
                task.status = "done"
                task.confirmed_at = now
                message = "任务已确认完成"
            elif action == "cancel":
                if status != "open":
                    raise ValueError("errand_status_conflict")
                if not is_publisher:
                    raise ValueError("errand_cancel_forbidden")
                task.status = "canceled"
                task.canceled_at = now
                message = "任务已撤销"
            else:
                raise ValueError("errand_action_invalid")

            db.add(task)
            db.commit()
            db.refresh(task)
            publisher = db.get(User, int(task.publisher_id))
            runner = db.get(User, int(task.runner_id)) if task.runner_id else None

        return {
            "item": self._to_item(task=task, viewer_user_id=user_id, publisher=publisher, runner=runner),
            "message": message,
        }


errand_service = ErrandService()
