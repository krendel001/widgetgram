import asyncio
import copy
import json
from typing import Any, Protocol

from aiogram import Bot

from .methods import EditMessageWidgetData
from .utils.state import assert_state_fits


StateDict = dict[str, Any]


class StateStorage(Protocol):
    async def get(self, chat_id: int, message_id: int) -> StateDict | None: ...
    async def put(self, chat_id: int, message_id: int, state: StateDict) -> None: ...
    async def drop(self, chat_id: int, message_id: int) -> None: ...


class MemoryStateStorage:
    def __init__(self) -> None:
        self._d: dict[tuple[int, int], StateDict] = {}
        self._lock = asyncio.Lock()

    async def get(self, chat_id: int, message_id: int) -> StateDict | None:
        async with self._lock:
            d = self._d.get((chat_id, message_id))
            return copy.deepcopy(d) if d is not None else None

    async def put(self, chat_id: int, message_id: int, state: StateDict) -> None:
        async with self._lock:
            self._d[(chat_id, message_id)] = copy.deepcopy(state)

    async def drop(self, chat_id: int, message_id: int) -> None:
        async with self._lock:
            self._d.pop((chat_id, message_id), None)


async def push_state(bot: Bot, chat_id: int, message_id: int, state: StateDict) -> None:
    payload = json.dumps(state, separators=(",", ":"), ensure_ascii=False)
    assert_state_fits(payload)
    await bot(EditMessageWidgetData(
        chat_id=chat_id,
        message_id=message_id,
        chat_data=payload,
    ))


__all__ = ["StateDict", "StateStorage", "MemoryStateStorage", "push_state"]
