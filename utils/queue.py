import asyncio
import logging
import time
from typing import Any, Awaitable, Callable, Hashable

log = logging.getLogger("widgetgram")

Sender = Callable[[], Awaitable[Any]]


class _Slot:
    __slots__ = ("sender", "handle", "task", "last_sent")

    def __init__(self) -> None:
        self.sender: Sender | None = None
        self.handle: asyncio.TimerHandle | None = None
        self.task: asyncio.Task[Any] | None = None
        self.last_sent: float = 0.0


class EditQueue:
    __slots__ = ("min_interval", "idle_ttl", "_slots")

    def __init__(self, min_interval: float = 1.1, idle_ttl: float = 60.0) -> None:
        self.min_interval = min_interval
        self.idle_ttl = idle_ttl
        self._slots: dict[Hashable, _Slot] = {}

    def push(self, key: Hashable, sender: Sender) -> None:
        now = time.monotonic()
        slot = self._slots.get(key)
        if slot is None:
            slot = _Slot()
            self._slots[key] = slot
        slot.sender = sender
        if slot.handle is not None or slot.task is not None:
            return
        delay = max(0.0, slot.last_sent + self.min_interval - now)
        loop = asyncio.get_running_loop()
        slot.handle = loop.call_later(delay, self._fire, key)

    def _fire(self, key: Hashable) -> None:
        slot = self._slots.get(key)
        if slot is None:
            return
        slot.handle = None
        sender = slot.sender
        slot.sender = None
        if sender is None:
            self._maybe_evict(key, slot)
            return
        slot.task = asyncio.create_task(self._run(key, sender))

    async def _run(self, key: Hashable, sender: Sender) -> None:
        slot = self._slots.get(key)
        try:
            await sender()
        except Exception as e:  # noqa: BLE001
            log.warning("edit failed for %s: %s", key, e)
        finally:
            if slot is None:
                return
            slot.task = None
            slot.last_sent = time.monotonic()
            if slot.sender is not None:
                loop = asyncio.get_running_loop()
                delay = max(0.0, slot.last_sent + self.min_interval - time.monotonic())
                slot.handle = loop.call_later(delay, self._fire, key)
            else:
                self._maybe_evict(key, slot)

    def _maybe_evict(self, key: Hashable, slot: _Slot) -> None:
        if slot.sender is not None or slot.handle is not None or slot.task is not None:
            return
        if time.monotonic() - slot.last_sent < self.idle_ttl:
            return
        self._slots.pop(key, None)

    async def flush(self, key: Hashable | None = None) -> None:
        keys = [key] if key is not None else list(self._slots.keys())
        for k in keys:
            while True:
                slot = self._slots.get(k)
                if slot is None:
                    break
                if slot.handle is not None:
                    slot.handle.cancel()
                    slot.handle = None
                    self._fire(k)
                    continue
                if slot.task is not None:
                    try:
                        await slot.task
                    except Exception:  # noqa: BLE001
                        pass
                    continue
                if slot.sender is None:
                    break

    def close(self) -> None:
        for slot in self._slots.values():
            if slot.handle is not None:
                slot.handle.cancel()
                slot.handle = None
            if slot.task is not None:
                slot.task.cancel()
        self._slots.clear()
