from __future__ import annotations

import threading
import time


class EvolutionRealtimeService:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._running = False
        self._pending = False
        self._last_run_at = 0.0
        self._debounce_seconds = 1.5
        self._min_interval_seconds = 8.0
        self._batch_limit = 8

    def notify_candidate(
        self,
        *,
        post_id: int,
        likes_count: int = 0,
        comments_count: int = 0,
        adopted: bool = False,
        reason: str = "",
    ) -> bool:
        qualifies = bool(adopted or int(likes_count or 0) >= 30 or int(comments_count or 0) >= 5)
        if not qualifies or int(post_id or 0) <= 0:
            return False
        return self.request_sync(reason=reason or f"post:{post_id}")

    def request_sync(self, reason: str = "") -> bool:
        del reason
        with self._lock:
            self._pending = True
            if self._running:
                return True
            self._running = True

        worker = threading.Thread(target=self._drain, name="evolution-realtime-sync", daemon=True)
        worker.start()
        return True

    def _drain(self) -> None:
        while True:
            with self._lock:
                if not self._pending:
                    self._running = False
                    return
                self._pending = False

            time.sleep(self._debounce_seconds)
            cooldown = max(0.0, self._min_interval_seconds - (time.monotonic() - self._last_run_at))
            if cooldown:
                time.sleep(cooldown)

            try:
                from app.services.evolution_service import evolution_service

                evolution_service.sync_high_quality_posts(
                    kb_id=1,
                    min_likes=30,
                    min_comments=5,
                    limit=self._batch_limit,
                    include_reviewed=False,
                )
            except Exception:
                pass
            finally:
                self._last_run_at = time.monotonic()


evolution_realtime_service = EvolutionRealtimeService()
